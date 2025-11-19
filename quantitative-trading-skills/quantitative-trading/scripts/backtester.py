#!/usr/bin/env python3
"""
Backtesting Engine for Quantitative Trading
Tests trading strategies on historical data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from data_fetcher import DataFetcher
from strategies import TradingStrategy

class Backtester:
    def __init__(self, initial_capital=100000, commission=0.001, slippage=0.001):
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = {}

    def backtest_strategy(self, data, strategy_name, strategy_params=None):
        """
        Backtest a single strategy

        Args:
            data (pd.DataFrame): Historical price data
            strategy_name (str): Name of the strategy
            strategy_params (dict): Parameters for the strategy

        Returns:
            dict: Backtest results
        """
        if strategy_params is None:
            strategy_params = {}

        # Initialize strategy and generate signals
        strategy = TradingStrategy(self.initial_capital)
        strategy_func = getattr(strategy, strategy_name.replace('-', '_') + '_strategy', None)

        if strategy_func is None:
            strategy_func = getattr(strategy, strategy_name.replace('-', '_'), None)

        if strategy_func is None:
            raise ValueError(f"Strategy '{strategy_name}' not found")

        # Generate signals
        if strategy_name == 'multi_strategy':
            signals_data = strategy.multi_strategy_signals(data, **strategy_params)
        else:
            signals_data = strategy_func(data.copy(), **strategy_params)

        # Simulate trading
        results = self._simulate_trading(signals_data, data)

        # Calculate performance metrics
        performance = self._calculate_performance_metrics(results)

        return {
            'signals': signals_data,
            'trades': results,
            'performance': performance,
            'strategy_name': strategy_name,
            'strategy_params': strategy_params
        }

    def _simulate_trading(self, signals_data, price_data):
        """
        Simulate trading based on signals
        """
        trades = []
        position = 0
        cash = self.initial_capital
        portfolio_value = []

        for i, (date, row) in enumerate(signals_data.iterrows()):
            current_price = price_data.loc[date, 'Close']

            # Apply slippage
            buy_price = current_price * (1 + self.slippage)
            sell_price = current_price * (1 - self.slippage)

            # Check for buy signal
            if row.get('Buy_Signal', False) and position <= 0:
                # Close existing short position
                if position < 0:
                    profit = (sell_price - self.entry_price) * abs(position)
                    commission_cost = abs(position) * sell_price * self.commission
                    cash += profit - commission_cost

                # Open long position
                position_size = cash // (buy_price * (1 + self.commission))
                if position_size > 0:
                    commission_cost = position_size * buy_price * self.commission
                    cash -= position_size * buy_price + commission_cost
                    position = position_size
                    self.entry_price = buy_price

                    trades.append({
                        'date': date,
                        'type': 'BUY',
                        'price': buy_price,
                        'quantity': position_size,
                        'cash_before': cash + position_size * buy_price,
                        'cash_after': cash
                    })

            # Check for sell signal
            elif row.get('Sell_Signal', False) and position >= 0:
                # Close existing long position
                if position > 0:
                    profit = (sell_price - self.entry_price) * position
                    commission_cost = position * sell_price * self.commission
                    cash += position * sell_price - commission_cost

                    trades.append({
                        'date': date,
                        'type': 'SELL',
                        'price': sell_price,
                        'quantity': position,
                        'cash_before': cash - position * sell_price,
                        'cash_after': cash
                    })

                # Open short position
                position_size = cash // (sell_price * (1 + self.commission))
                if position_size > 0:
                    commission_cost = position_size * sell_price * self.commission
                    cash -= commission_cost
                    position = -position_size
                    self.entry_price = sell_price

                    trades.append({
                        'date': date,
                        'type': 'SHORT',
                        'price': sell_price,
                        'quantity': position_size,
                        'cash_before': cash,
                        'cash_after': cash
                    })

            # Update portfolio value
            if position != 0:
                portfolio_value.append(cash + position * current_price)
            else:
                portfolio_value.append(cash)

        # Create trades DataFrame
        trades_df = pd.DataFrame(trades)

        # Create portfolio value series
        portfolio_series = pd.Series(portfolio_value, index=signals_data.index)

        return {
            'trades': trades_df,
            'portfolio_value': portfolio_series
        }

    def _calculate_performance_metrics(self, results):
        """
        Calculate performance metrics
        """
        portfolio_value = results['portfolio_value']
        returns = portfolio_value.pct_change().dropna()

        # Basic metrics
        total_return = (portfolio_value.iloc[-1] / self.initial_capital - 1) * 100
        annualized_return = ((portfolio_value.iloc[-1] / self.initial_capital) ** (252 / len(portfolio_value)) - 1) * 100
        volatility = returns.std() * np.sqrt(252) * 100

        # Risk-adjusted metrics
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else 0
        downside_returns = returns[returns < 0]
        sortino_ratio = (returns.mean() / downside_returns.std()) * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() != 0 else 0

        # Drawdown
        cumulative_max = portfolio_value.cummax()
        drawdown = (portfolio_value - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min() * 100

        # Trade statistics
        trades = results['trades']
        if len(trades) > 0:
            num_trades = len(trades)
            profitable_trades = 0

            for i in range(0, len(trades) - 1, 2):
                if i + 1 < len(trades):
                    if trades.iloc[i]['type'] in ['BUY', 'SHORT']:
                        entry_price = trades.iloc[i]['price']
                        exit_price = trades.iloc[i + 1]['price']
                        quantity = trades.iloc[i]['quantity']

                        if trades.iloc[i]['type'] == 'BUY':
                            profit = (exit_price - entry_price) * quantity
                        else:  # SHORT
                            profit = (entry_price - exit_price) * quantity

                        if profit > 0:
                            profitable_trades += 1

            win_rate = (profitable_trades / (num_trades // 2)) * 100 if num_trades > 0 else 0
        else:
            num_trades = 0
            win_rate = 0

        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'max_drawdown': max_drawdown,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'final_portfolio_value': portfolio_value.iloc[-1],
            'initial_capital': self.initial_capital
        }

    def compare_strategies(self, data, strategies_config):
        """
        Compare multiple strategies

        Args:
            data (pd.DataFrame): Historical price data
            strategies_config (dict): Dictionary of strategy configurations

        Returns:
            dict: Comparison results
        """
        comparison_results = {}

        for strategy_name, config in strategies_config.items():
            try:
                print(f"Backtesting {strategy_name}...")
                results = self.backtest_strategy(data, strategy_name, config.get('params', {}))
                comparison_results[strategy_name] = results
                print(f"✓ {strategy_name}: Total Return {results['performance']['total_return']:.2f}%")
            except Exception as e:
                print(f"✗ Error backtesting {strategy_name}: {e}")
                continue

        # Create comparison table
        comparison_table = self._create_comparison_table(comparison_results)

        return {
            'results': comparison_results,
            'comparison_table': comparison_table
        }

    def _create_comparison_table(self, results):
        """
        Create a comparison table of strategy performance
        """
        metrics = ['total_return', 'annualized_return', 'volatility', 'sharpe_ratio',
                  'sortino_ratio', 'max_drawdown', 'num_trades', 'win_rate']

        comparison_data = []

        for strategy_name, result in results.items():
            performance = result['performance']
            row = [strategy_name]

            for metric in metrics:
                value = performance.get(metric, 0)
                if metric in ['total_return', 'annualized_return', 'volatility', 'max_drawdown', 'win_rate']:
                    row.append(f"{value:.2f}%")
                elif metric in ['sharpe_ratio', 'sortino_ratio']:
                    row.append(f"{value:.2f}")
                else:
                    row.append(f"{value}")

            comparison_data.append(row)

        df = pd.DataFrame(comparison_data, columns=['Strategy'] + [m.replace('_', ' ').title() for m in metrics])
        return df

    def monte_carlo_simulation(self, data, strategy_name, strategy_params, num_simulations=1000):
        """
        Perform Monte Carlo simulation for strategy robustness
        """
        strategy = TradingStrategy(self.initial_capital)
        original_returns = data['Close'].pct_change().dropna()

        simulation_results = []

        for i in range(num_simulations):
            # Generate random returns with same distribution
            np.random.seed(i)
            random_returns = np.random.choice(original_returns, size=len(original_returns), replace=True)

            # Generate synthetic price data
            synthetic_prices = self.initial_capital * (1 + random_returns).cumprod()

            # Create synthetic DataFrame
            synthetic_data = data.copy()
            synthetic_data['Close'] = synthetic_prices

            # Backtest strategy on synthetic data
            try:
                result = self.backtest_strategy(synthetic_data, strategy_name, strategy_params)
                simulation_results.append(result['performance'])
            except Exception as e:
                print(f"Simulation {i} failed: {e}")
                continue

        # Calculate statistics from simulations
        if simulation_results:
            metrics = ['total_return', 'sharpe_ratio', 'max_drawdown']
            stats = {}

            for metric in metrics:
                values = [result[metric] for result in simulation_results]
                stats[metric] = {
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'percentile_5': np.percentile(values, 5),
                    'percentile_95': np.percentile(values, 95)
                }

            return {
                'num_simulations': num_simulations,
                'successful_simulations': len(simulation_results),
                'statistics': stats
            }
        else:
            return None

    def plot_results(self, backtest_results, benchmark=None):
        """
        Plot backtest results
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Portfolio Value
        portfolio_value = backtest_results['trades']['portfolio_value']
        axes[0, 0].plot(portfolio_value.index, portfolio_value, label='Strategy', linewidth=2)

        if benchmark is not None:
            benchmark_returns = (benchmark / benchmark.iloc[0]) * self.initial_capital
            axes[0, 0].plot(benchmark_returns.index, benchmark_returns, label='Benchmark', alpha=0.7)

        axes[0, 0].set_title('Portfolio Value Over Time')
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        # Drawdown
        cumulative_max = portfolio_value.cummax()
        drawdown = (portfolio_value - cumulative_max) / cumulative_max * 100
        axes[0, 1].fill_between(drawdown.index, drawdown.values, 0, alpha=0.3, color='red')
        axes[0, 1].set_title('Drawdown (%)')
        axes[0, 1].grid(True)

        # Returns Distribution
        returns = portfolio_value.pct_change().dropna()
        axes[1, 0].hist(returns, bins=50, alpha=0.7, density=True)
        axes[1, 0].set_title('Returns Distribution')
        axes[1, 0].grid(True)

        # Performance Summary
        performance = backtest_results['performance']
        metrics_text = f"""
        Total Return: {performance['total_return']:.2f}%
        Annualized Return: {performance['annualized_return']:.2f}%
        Volatility: {performance['volatility']:.2f}%
        Sharpe Ratio: {performance['sharpe_ratio']:.2f}
        Max Drawdown: {performance['max_drawdown']:.2f}%
        Number of Trades: {performance['num_trades']}
        Win Rate: {performance['win_rate']:.2f}%
        """

        axes[1, 1].text(0.1, 0.5, metrics_text, transform=axes[1, 1].transAxes,
                        fontsize=12, verticalalignment='center')
        axes[1, 1].set_title('Performance Summary')
        axes[1, 1].axis('off')

        plt.tight_layout()
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Backtest trading strategies')
    parser.add_argument('--ticker', '-t', type=str, required=True, help='Stock ticker')
    parser.add_argument('--strategy', '-s', type=str, help='Single strategy to test')
    parser.add_argument('--compare', action='store_true', help='Compare multiple strategies')
    parser.add_argument('--period', type=str, default='2y', help='Period for backtesting')
    parser.add_argument('--initial-capital', type=float, default=100000, help='Initial capital')
    parser.add_argument('--commission', type=float, default=0.001, help='Commission rate')
    parser.add_argument('--monte-carlo', action='store_true', help='Run Monte Carlo simulation')
    parser.add_argument('--simulations', type=int, default=1000, help='Number of Monte Carlo simulations')
    parser.add_argument('--plot', action='store_true', help='Plot results')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(args.ticker, period=args.period)

    if data is None:
        print(f"Could not fetch data for {args.ticker}")
        return

    # Initialize backtester
    backtester = Backtester(args.initial_capital, args.commission)

    try:
        if args.compare:
            # Compare multiple strategies
            strategies_config = {
                'moving_average_crossover': {'params': {'fast_window': 20, 'slow_window': 50}},
                'rsi': {'params': {'rsi_window': 14, 'oversold': 30, 'overbought': 70}},
                'macd': {'params': {'fast': 12, 'slow': 26, 'signal': 9}},
                'bollinger': {'params': {'window': 20, 'num_std': 2}},
                'multi_strategy': {'params': {}}
            }

            comparison_results = backtester.compare_strategies(data, strategies_config)

            print(f"\nStrategy Comparison for {args.ticker}:")
            print("=" * 80)
            print(comparison_results['comparison_table'].to_string(index=False))

            if args.output:
                comparison_results['comparison_table'].to_csv(args.output, index=False)
                print(f"\nComparison table saved to {args.output}")

        elif args.strategy:
            # Single strategy backtest
            results = backtester.backtest_strategy(data, args.strategy)

            print(f"\nBacktest Results for {args.strategy} on {args.ticker}:")
            print("=" * 60)
            performance = results['performance']

            for key, value in performance.items():
                if key in ['total_return', 'annualized_return', 'volatility', 'max_drawdown', 'win_rate']:
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}%")
                elif key in ['sharpe_ratio', 'sortino_ratio']:
                    print(f"{key.replace('_', ' ').title()}: {value:.2f}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value}")

            if args.monte_carlo:
                print(f"\nRunning Monte Carlo simulation with {args.simulations} iterations...")
                mc_results = backtester.monte_carlo_simulation(data, args.strategy, {}, args.simulations)

                if mc_results:
                    print("Monte Carlo Results:")
                    for metric, stats in mc_results['statistics'].items():
                        print(f"{metric.replace('_', ' ').title()}:")
                        print(f"  Mean: {stats['mean']:.2f}")
                        print(f"  5th Percentile: {stats['percentile_5']:.2f}")
                        print(f"  95th Percentile: {stats['percentile_95']:.2f}")

            if args.plot:
                backtester.plot_results(results)

        else:
            print("Please specify either --strategy or --compare")
            return

    except Exception as e:
        print(f"Error during backtesting: {e}")


if __name__ == "__main__":
    main()
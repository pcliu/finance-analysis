#!/usr/bin/env python3
"""
Portfolio Analysis and Optimization for Quantitative Trading
Analyzes portfolio performance, risk metrics, and optimization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import argparse
from data_fetcher import DataFetcher

class PortfolioAnalyzer:
    def __init__(self, risk_free_rate=0.02):
        self.risk_free_rate = risk_free_rate
        self.fetcher = DataFetcher()

    def create_portfolio_data(self, tickers, period='1y'):
        """
        Create portfolio data from multiple stocks

        Args:
            tickers (list): List of ticker symbols
            period (str): Period for data fetching

        Returns:
            pd.DataFrame: Portfolio data with all tickers
        """
        portfolio_data = {}

        for ticker in tickers:
            data = self.fetcher.fetch_stock_data(ticker, period=period)
            if data is not None and not data.empty:
                portfolio_data[ticker] = data['Close']

        if not portfolio_data:
            return None

        # Create aligned DataFrame
        portfolio_df = pd.DataFrame(portfolio_data)
        portfolio_df = portfolio_df.dropna()

        return portfolio_df

    def calculate_returns(self, price_data):
        """
        Calculate daily returns for portfolio

        Args:
            price_data (pd.DataFrame): Price data for multiple assets

        Returns:
            pd.DataFrame: Daily returns
        """
        returns = price_data.pct_change().dropna()
        return returns

    def calculate_portfolio_metrics(self, returns, weights=None):
        """
        Calculate portfolio risk and return metrics

        Args:
            returns (pd.DataFrame): Asset returns
            weights (np.array): Portfolio weights

        Returns:
            dict: Portfolio metrics
        """
        if weights is None:
            weights = np.array([1/len(returns.columns)] * len(returns.columns))

        # Basic metrics
        portfolio_returns = (returns * weights).sum(axis=1)
        mean_return = portfolio_returns.mean() * 252  # Annualized
        volatility = portfolio_returns.std() * np.sqrt(252)  # Annualized

        # Risk-adjusted metrics
        sharpe_ratio = (mean_return - self.risk_free_rate) / volatility

        # Downside deviation for Sortino ratio
        downside_returns = portfolio_returns[portfolio_returns < 0]
        downside_deviation = downside_returns.std() * np.sqrt(252)
        sortino_ratio = (mean_return - self.risk_free_rate) / downside_deviation if downside_deviation != 0 else 0

        # Value at Risk and Conditional VaR
        var_95 = np.percentile(portfolio_returns, 5)
        var_99 = np.percentile(portfolio_returns, 1)
        cvar_95 = portfolio_returns[portfolio_returns <= var_95].mean()
        cvar_99 = portfolio_returns[portfolio_returns <= var_99].mean()

        # Maximum drawdown
        cumulative_returns = (1 + portfolio_returns).cumprod()
        cumulative_max = cumulative_returns.cummax()
        drawdown = (cumulative_returns - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()

        # Beta and Alpha (compared to market - use first asset as proxy)
        market_returns = returns.iloc[:, 0]
        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)
        beta = covariance / market_variance if market_variance != 0 else 0
        alpha = mean_return - self.risk_free_rate - beta * (market_returns.mean() * 252 - self.risk_free_rate)

        return {
            'weights': weights,
            'expected_return': mean_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'max_drawdown': max_drawdown,
            'beta': beta,
            'alpha': alpha,
            'portfolio_returns': portfolio_returns
        }

    def optimize_portfolio(self, returns, optimization_method='sharpe', target_return=None):
        """
        Optimize portfolio weights

        Args:
            returns (pd.DataFrame): Asset returns
            optimization_method (str): 'sharpe', 'min_volatility', 'target_return', 'risk_parity'
            target_return (float): Target return for target_return optimization

        Returns:
            dict: Optimization results
        """
        num_assets = len(returns.columns)
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1
        bounds = tuple((0, 1) for _ in range(num_assets))  # No short selling

        # Initial guess (equal weights)
        initial_weights = np.array([1/num_assets] * num_assets)

        def objective_function(weights):
            metrics = self.calculate_portfolio_metrics(returns, weights)

            if optimization_method == 'sharpe':
                return -metrics['sharpe_ratio']  # Negative because we want to maximize
            elif optimization_method == 'min_volatility':
                return metrics['volatility']
            elif optimization_method == 'target_return':
                # Penalize deviation from target return and high volatility
                return abs(metrics['expected_return'] - target_return) + metrics['volatility']
            elif optimization_method == 'risk_parity':
                # Risk parity: equal risk contribution
                portfolio_vol = metrics['volatility']
                marginal_contrib = np.dot(returns.cov(), weights)
                risk_contrib = weights * marginal_contrib / portfolio_vol**2
                return np.sum((risk_contrib - np.mean(risk_contrib))**2)
            else:
                raise ValueError(f"Unknown optimization method: {optimization_method}")

        if optimization_method == 'target_return' and target_return is None:
            raise ValueError("Target return must be specified for target_return optimization")

        # Optimize
        result = minimize(objective_function, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        if result.success:
            optimal_weights = result.x
            optimal_metrics = self.calculate_portfolio_metrics(returns, optimal_weights)

            return {
                'success': True,
                'weights': optimal_weights,
                'metrics': optimal_metrics,
                'asset_names': returns.columns.tolist()
            }
        else:
            return {
                'success': False,
                'message': result.message
            }

    def calculate_efficient_frontier(self, returns, num_portfolios=100):
        """
        Calculate efficient frontier

        Args:
            returns (pd.DataFrame): Asset returns
            num_portfolios (int): Number of portfolios to generate

        Returns:
            dict: Efficient frontier data
        """
        num_assets = len(returns.columns)
        results = []

        # Generate random portfolios
        for _ in range(num_portfolios):
            weights = np.random.random(num_assets)
            weights = weights / np.sum(weights)  # Normalize

            metrics = self.calculate_portfolio_metrics(returns, weights)
            results.append({
                'weights': weights,
                'return': metrics['expected_return'],
                'volatility': metrics['volatility'],
                'sharpe_ratio': metrics['sharpe_ratio']
            })

        # Find optimal portfolios
        results_df = pd.DataFrame(results)
        max_sharpe = results_df.loc[results_df['sharpe_ratio'].idxmax()]
        min_vol = results_df.loc[results_df['volatility'].idxmin()]

        return {
            'portfolios': results_df,
            'max_sharpe_portfolio': max_sharpe,
            'min_volatility_portfolio': min_vol,
            'asset_names': returns.columns.tolist()
        }

    def calculate_risk_metrics(self, returns, weights=None):
        """
        Calculate detailed risk metrics

        Args:
            returns (pd.DataFrame): Asset returns
            weights (np.array): Portfolio weights

        Returns:
            dict: Risk metrics
        """
        if weights is None:
            weights = np.array([1/len(returns.columns)] * len(returns.columns))

        # Calculate portfolio returns
        portfolio_returns = (returns * weights).sum(axis=1)

        # VaR and CVaR at different confidence levels
        var_levels = [0.90, 0.95, 0.99]
        risk_metrics = {}

        for level in var_levels:
            var = np.percentile(portfolio_returns, (1-level) * 100)
            cvar = portfolio_returns[portfolio_returns <= var].mean()
            risk_metrics[f'var_{int(level*100)}'] = var
            risk_metrics[f'cvar_{int(level*100)}'] = cvar

        # Drawdown metrics
        cumulative = (1 + portfolio_returns).cumprod()
        cumulative_max = cumulative.cummax()
        drawdown = (cumulative - cumulative_max) / cumulative_max

        risk_metrics['max_drawdown'] = drawdown.min()
        risk_metrics['avg_drawdown'] = drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0
        risk_metrics['drawdown_duration'] = (drawdown < 0).astype(int).groupby((drawdown >= 0).cumsum()).sum().max()

        # Correlation and diversification metrics
        correlation_matrix = returns.corr()
        avg_correlation = correlation_matrix.values[np.triu_indices(len(correlation_matrix), 1)].mean()
        diversification_ratio = (np.std(weights) * np.sqrt(np.sum(np.diag(returns.cov())))) / np.sqrt(np.dot(weights, np.dot(returns.cov(), weights)))

        risk_metrics['avg_correlation'] = avg_correlation
        risk_metrics['diversification_ratio'] = diversification_ratio

        # Component VaR (risk contribution)
        portfolio_vol = portfolio_returns.std() * np.sqrt(252)
        marginal_var = np.dot(returns.cov() * 252, weights)
        component_var = weights * marginal_var

        risk_metrics['component_var'] = component_var
        risk_metrics['marginal_var'] = marginal_var

        return risk_metrics

    def backtest_portfolio(self, tickers, weights=None, rebalance_frequency='monthly', period='2y'):
        """
        Backtest a portfolio strategy

        Args:
            tickers (list): List of ticker symbols
            weights (list): Portfolio weights
            rebalance_frequency (str): Rebalancing frequency
            period (str): Backtest period

        Returns:
            dict: Backtest results
        """
        # Fetch data
        price_data = self.create_portfolio_data(tickers, period)

        if price_data is None:
            return {'success': False, 'message': 'Could not fetch data'}

        if weights is None:
            weights = [1/len(tickers)] * len(tickers)

        # Convert to numpy array
        weights = np.array(weights)

        # Calculate daily returns
        returns = self.calculate_returns(price_data)

        # Simulate portfolio with rebalancing
        portfolio_value = []
        current_weights = weights.copy()
        current_value = 100000  # Starting value

        # Determine rebalancing dates
        if rebalance_frequency == 'monthly':
            rebalance_dates = price_data.resample('M').first().index
        elif rebalance_frequency == 'quarterly':
            rebalance_dates = price_data.resample('Q').first().index
        elif rebalance_frequency == 'yearly':
            rebalance_dates = price_data.resample('Y').first().index
        else:
            rebalance_dates = []

        for date, row in returns.iterrows():
            # Daily portfolio return
            daily_return = (row * current_weights).sum()
            current_value *= (1 + daily_return)

            # Rebalancing
            if date in rebalance_dates:
                current_weights = weights.copy()

            portfolio_value.append(current_value)

        portfolio_series = pd.Series(portfolio_value, index=returns.index)

        # Calculate performance metrics
        portfolio_returns = portfolio_series.pct_change().dropna()
        total_return = (portfolio_series.iloc[-1] / portfolio_series.iloc[0] - 1) * 100
        annualized_return = ((portfolio_series.iloc[-1] / portfolio_series.iloc[0]) ** (252 / len(portfolio_series)) - 1) * 100
        volatility = portfolio_returns.std() * np.sqrt(252) * 100
        sharpe_ratio = (portfolio_returns.mean() / portfolio_returns.std()) * np.sqrt(252) if portfolio_returns.std() != 0 else 0

        # Drawdown
        cumulative_max = portfolio_series.cummax()
        drawdown = (portfolio_series - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min() * 100

        return {
            'success': True,
            'portfolio_value': portfolio_series,
            'returns': portfolio_returns,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'weights': weights,
            'tickers': tickers
        }

    def sector_analysis(self, sector_tickers, period='1y'):
        """
        Analyze sector performance and correlations

        Args:
            sector_tickers (dict): Dictionary with sectors as keys and ticker lists as values
            period (str): Analysis period

        Returns:
            dict: Sector analysis results
        """
        sector_data = {}
        sector_returns = {}

        for sector, tickers in sector_tickers.items():
            data = self.create_portfolio_data(tickers, period)
            if data is not None:
                sector_data[sector] = data
                returns = self.calculate_returns(data)
                sector_returns[sector] = returns.mean(axis=1)  # Equal-weighted sector returns

        # Create sector returns DataFrame
        sector_returns_df = pd.DataFrame(sector_returns).dropna()

        # Calculate sector correlations
        sector_correlations = sector_returns_df.corr()

        # Calculate sector performance
        sector_performance = {}
        for sector in sector_returns_df.columns:
            sector_ret = sector_returns_df[sector]
            sector_performance[sector] = {
                'total_return': ((1 + sector_ret).prod() - 1) * 100,
                'annualized_return': sector_ret.mean() * 252 * 100,
                'volatility': sector_ret.std() * np.sqrt(252) * 100,
                'sharpe_ratio': (sector_ret.mean() / sector_ret.std()) * np.sqrt(252) if sector_ret.std() != 0 else 0
            }

        return {
            'sector_data': sector_data,
            'sector_returns': sector_returns_df,
            'sector_correlations': sector_correlations,
            'sector_performance': sector_performance
        }

    def plot_results(self, results):
        """
        Plot portfolio analysis results
        """
        if 'efficient_frontier' in results:
            # Plot efficient frontier
            ef_data = results['efficient_frontier']
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

            # Efficient Frontier
            ax1.scatter(ef_data['portfolios']['volatility'] * 100,
                       ef_data['portfolios']['return'] * 100,
                       c=ef_data['portfolios']['sharpe_ratio'],
                       cmap='viridis', alpha=0.6)
            ax1.scatter(ef_data['max_sharpe_portfolio']['volatility'] * 100,
                       ef_data['max_sharpe_portfolio']['return'] * 100,
                       color='red', s=100, marker='*', label='Max Sharpe')
            ax1.scatter(ef_data['min_volatility_portfolio']['volatility'] * 100,
                       ef_data['min_volatility_portfolio']['return'] * 100,
                       color='blue', s=100, marker='*', label='Min Volatility')
            ax1.set_xlabel('Volatility (%)')
            ax1.set_ylabel('Expected Return (%)')
            ax1.set_title('Efficient Frontier')
            ax1.legend()
            plt.colorbar(ax1.collections[0], ax=ax1, label='Sharpe Ratio')

            # Portfolio Weights
            optimal_weights = ef_data['max_sharpe_portfolio']['weights']
            asset_names = ef_data['asset_names']
            ax2.pie(optimal_weights, labels=asset_names, autopct='%1.1f%%')
            ax2.set_title('Optimal Portfolio Weights')

        plt.tight_layout()
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Analyze and optimize portfolios')
    parser.add_argument('--tickers', '-t', type=str, required=True, help='Comma-separated ticker symbols')
    parser.add_argument('--weights', type=str, help='Comma-separated weights (must match tickers)')
    parser.add_argument('--period', type=str, default='1y', help='Analysis period')
    parser.add_argument('--optimize', choices=['sharpe', 'min_volatility', 'risk_parity'], help='Optimization method')
    parser.add_argument('--efficient-frontier', action='store_true', help='Calculate efficient frontier')
    parser.add_argument('--risk-metrics', action='store_true', help='Calculate detailed risk metrics')
    parser.add_argument('--backtest', action='store_true', help='Backtest portfolio')
    parser.add_argument('--rebalance', choices=['daily', 'monthly', 'quarterly', 'yearly'], default='monthly', help='Rebalancing frequency')
    parser.add_argument('--plot', action='store_true', help='Plot results')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Parse tickers and weights
    tickers = [t.strip() for t in args.tickers.split(',')]
    weights = None

    if args.weights:
        weights = [float(w.strip()) for w in args.weights.split(',')]
        if len(weights) != len(tickers):
            print("Number of weights must match number of tickers")
            return

        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]

    # Initialize analyzer
    analyzer = PortfolioAnalyzer()

    try:
        # Create portfolio data
        print(f"Fetching data for {len(tickers)} tickers...")
        price_data = analyzer.create_portfolio_data(tickers, args.period)

        if price_data is None:
            print("Could not fetch data for specified tickers")
            return

        returns = analyzer.calculate_returns(price_data)
        print(f"Successfully created portfolio with {len(tickers)} assets")

        # Basic portfolio metrics
        if weights:
            metrics = analyzer.calculate_portfolio_metrics(returns, np.array(weights))
            print(f"\nPortfolio Metrics with Custom Weights:")
            print(f"Expected Return: {metrics['expected_return']:.2f}%")
            print(f"Volatility: {metrics['volatility']:.2f}%")
            print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
            print(f"Sortino Ratio: {metrics['sortino_ratio']:.2f}")
            print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")

        # Portfolio optimization
        if args.optimize:
            print(f"\nOptimizing portfolio ({args.optimize} optimization)...")
            optimization_result = analyzer.optimize_portfolio(returns, args.optimize)

            if optimization_result['success']:
                opt_metrics = optimization_result['metrics']
                opt_weights = optimization_result['weights']
                asset_names = optimization_result['asset_names']

                print("Optimization Results:")
                print(f"Expected Return: {opt_metrics['expected_return']:.2f}%")
                print(f"Volatility: {opt_metrics['volatility']:.2f}%")
                print(f"Sharpe Ratio: {opt_metrics['sharpe_ratio']:.2f}")

                print("\nOptimal Weights:")
                for name, weight in zip(asset_names, opt_weights):
                    print(f"{name}: {weight:.2%}")

        # Efficient frontier
        if args.efficient_frontier:
            print("\nCalculating efficient frontier...")
            ef_results = analyzer.calculate_efficient_frontier(returns, num_portfolios=200)

            print("Efficient Frontier Results:")
            max_sharpe = ef_results['max_sharpe_portfolio']
            min_vol = ef_results['min_volatility_portfolio']

            print(f"\nMax Sharpe Portfolio:")
            print(f"Return: {max_sharpe['return']:.2f}%, Volatility: {max_sharpe['volatility']:.2f}%, Sharpe: {max_sharpe['sharpe_ratio']:.2f}")

            print(f"\nMin Volatility Portfolio:")
            print(f"Return: {min_vol['return']:.2f}%, Volatility: {min_vol['volatility']:.2f}%, Sharpe: {min_vol['sharpe_ratio']:.2f}")

            if args.plot:
                analyzer.plot_results({'efficient_frontier': ef_results})

        # Risk metrics
        if args.risk_metrics:
            risk_metrics = analyzer.calculate_risk_metrics(returns, np.array(weights) if weights else None)

            print(f"\nRisk Metrics:")
            print(f"95% VaR: {risk_metrics['var_95']:.2f}%")
            print(f"99% VaR: {risk_metrics['var_99']:.2f}%")
            print(f"95% CVaR: {risk_metrics['cvar_95']:.2f}%")
            print(f"99% CVaR: {risk_metrics['cvar_99']:.2f}%")
            print(f"Max Drawdown: {risk_metrics['max_drawdown']:.2f}%")
            print(f"Average Correlation: {risk_metrics['avg_correlation']:.3f}")
            print(f"Diversification Ratio: {risk_metrics['diversification_ratio']:.3f}")

        # Backtesting
        if args.backtest:
            print(f"\nBacktesting portfolio...")
            backtest_results = analyzer.backtest_portfolio(tickers, weights, args.rebalance, args.period)

            if backtest_results['success']:
                print(f"Backtest Results:")
                print(f"Total Return: {backtest_results['total_return']:.2f}%")
                print(f"Annualized Return: {backtest_results['annualized_return']:.2f}%")
                print(f"Volatility: {backtest_results['volatility']:.2f}%")
                print(f"Sharpe Ratio: {backtest_results['sharpe_ratio']:.2f}")
                print(f"Max Drawdown: {backtest_results['max_drawdown']:.2f}%")

                if args.plot:
                    plt.figure(figsize=(12, 6))
                    backtest_results['portfolio_value'].plot()
                    plt.title('Portfolio Value Over Time')
                    plt.ylabel('Portfolio Value')
                    plt.grid(True)
                    plt.show()

    except Exception as e:
        print(f"Error during portfolio analysis: {e}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Risk Management Tools for Quantitative Trading
Comprehensive risk assessment and management utilities
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from scipy.optimize import minimize
import argparse

try:
    from .data_fetcher import DataFetcher
except ImportError:
    from data_fetcher import DataFetcher

class RiskManager:
    def __init__(self, confidence_level=0.95):
        self.confidence_level = confidence_level
        self.fetcher = DataFetcher()

    def calculate_var(self, returns: pd.Series, method: str = 'historical', confidence_level: float = None) -> float:
        """
        Calculate Value at Risk (VaR)

        Args:
            returns (pd.Series): Portfolio or asset returns
            method (str): 'historical', 'parametric', 'monte_carlo'
            confidence_level (float): Confidence level (0.95, 0.99, etc.)

        Returns:
            float: VaR value
        """
        if confidence_level is None:
            confidence_level = self.confidence_level

        if method == 'historical':
            # Historical simulation
            var = np.percentile(returns, (1 - confidence_level) * 100)

        elif method == 'parametric':
            # Parametric (normal distribution)
            mean = returns.mean()
            std = returns.std()
            z_score = stats.norm.ppf(1 - confidence_level)
            var = mean + z_score * std

        elif method == 'monte_carlo':
            # Monte Carlo simulation
            num_simulations = 10000
            mean = returns.mean()
            std = returns.std()

            simulated_returns = np.random.normal(mean, std, num_simulations)
            var = np.percentile(simulated_returns, (1 - confidence_level) * 100)

        else:
            raise ValueError(f"Unknown VaR method: {method}")

        return var

    def calculate_cvar(self, returns: pd.Series, var: float = None, confidence_level: float = None) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall

        Args:
            returns (pd.Series): Portfolio or asset returns
            var (float): VaR value (if None, will be calculated)
            confidence_level (float): Confidence level

        Returns:
            float: CVaR value
        """
        if confidence_level is None:
            confidence_level = self.confidence_level

        if var is None:
            var = self.calculate_var(returns, 'historical', confidence_level)

        # CVaR is the mean of returns below VaR
        tail_losses = returns[returns <= var]
        cvar = tail_losses.mean() if len(tail_losses) > 0 else var

        return cvar

    def calculate_drawdown_metrics(self, series: pd.Series, is_returns: bool = True) -> dict:
        """
        Calculate comprehensive drawdown metrics.

        Args:
            series (pd.Series): Return series or cumulative price series
            is_returns (bool): Whether ``series`` represents arithmetic returns

        Returns:
            dict: Drawdown metrics
        """
        if isinstance(series, pd.DataFrame):
            series = series.squeeze()

        if not isinstance(series, pd.Series):
            series = pd.Series(series)

        series = series.dropna()

        if series.empty:
            raise ValueError("Input series for drawdown metrics cannot be empty")

        cumulative = (1 + series).cumprod() if is_returns else series

        # Calculate drawdown
        cumulative_max = cumulative.cummax()
        drawdown = (cumulative - cumulative_max) / cumulative_max

        # Drawdown metrics
        max_drawdown = drawdown.min()
        avg_drawdown = drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0

        # Drawdown duration analysis
        drawdown_periods = []
        in_drawdown = False
        start_date = None

        for date, dd in drawdown.items():
            if dd < 0 and not in_drawdown:
                in_drawdown = True
                start_date = date
            elif dd >= 0 and in_drawdown:
                in_drawdown = False
                duration = (date - start_date).days
                drawdown_periods.append(duration)

        if in_drawdown:
            current_duration = (drawdown.index[-1] - start_date).days
            drawdown_periods.append(current_duration)

        max_drawdown_duration = max(drawdown_periods) if drawdown_periods else 0
        avg_drawdown_duration = np.mean(drawdown_periods) if drawdown_periods else 0

        # Time to recovery (from max drawdown)
        max_dd_end_date = drawdown.idxmin()
        if max_dd_end_date < cumulative.index[-1]:
            recovery_value = cumulative.loc[max_dd_end_date]
            recovery_series = cumulative.loc[max_dd_end_date:]
            time_to_recovery = (recovery_series[recovery_series >= recovery_value].index[0] - max_dd_end_date).days if len(recovery_series[recovery_series >= recovery_value]) > 0 else np.nan
        else:
            time_to_recovery = np.nan

        return {
            'max_drawdown': max_drawdown,
            'avg_drawdown': avg_drawdown,
            'max_drawdown_duration': max_drawdown_duration,
            'avg_drawdown_duration': avg_drawdown_duration,
            'time_to_recovery': time_to_recovery,
            'drawdown_periods_count': len(drawdown_periods),
            'current_drawdown': drawdown.iloc[-1]
        }

    def calculate_risk_adjusted_metrics(self, returns: pd.Series, benchmark_returns: pd.Series = None, risk_free_rate: float = 0.02) -> dict:
        """
        Calculate risk-adjusted performance metrics

        Args:
            returns (pd.Series): Portfolio returns
            benchmark_returns (pd.Series): Benchmark returns
            risk_free_rate (float): Risk-free rate

        Returns:
            dict: Risk-adjusted metrics
        """
        # Basic metrics
        mean_return = returns.mean() * 252  # Annualized
        volatility = returns.std() * np.sqrt(252)  # Annualized

        # Sharpe ratio
        excess_return = mean_return - risk_free_rate
        sharpe_ratio = excess_return / volatility if volatility != 0 else 0

        # Sortino ratio
        downside_returns = returns[returns < 0]
        downside_volatility = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = excess_return / downside_volatility if downside_volatility != 0 else 0

        # Calmar ratio
        if isinstance(returns, pd.Series) and returns.min() < 0:
            cumulative = (1 + returns).cumprod()
        else:
            cumulative = returns

        drawdown_metrics = self.calculate_drawdown_metrics(cumulative, is_returns=False)
        calmar_ratio = mean_return / abs(drawdown_metrics['max_drawdown']) if drawdown_metrics['max_drawdown'] != 0 else 0

        # Information ratio (if benchmark provided)
        information_ratio = 0
        tracking_error = 0
        if benchmark_returns is not None:
            active_returns = returns - benchmark_returns
            information_ratio = active_returns.mean() / active_returns.std() * np.sqrt(252) if active_returns.std() != 0 else 0
            tracking_error = active_returns.std() * np.sqrt(252)

        # Treynor ratio (if benchmark provided)
        treynor_ratio = 0
        if benchmark_returns is not None:
            # Calculate beta
            covariance = np.cov(returns, benchmark_returns)[0, 1]
            benchmark_variance = np.var(benchmark_returns)
            beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
            treynor_ratio = excess_return / beta if beta != 0 else 0

        return {
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio,
            'calmar_ratio': calmar_ratio,
            'information_ratio': information_ratio,
            'treynor_ratio': treynor_ratio,
            'tracking_error': tracking_error,
            'volatility': volatility,
            'downside_volatility': downside_volatility,
            'beta': beta if 'beta' in locals() else 0
        }

    def stress_testing(self, returns: pd.Series, stress_scenarios: dict = None) -> dict:
        """
        Perform stress testing on portfolio

        Args:
            returns (pd.Series): Portfolio returns
            stress_scenarios (dict): Custom stress scenarios

        Returns:
            dict: Stress test results
        """
        if stress_scenarios is None:
            stress_scenarios = {
                'market_crash': {'return': -0.20, 'vol_multiplier': 2.0},
                'volatility_spike': {'return': 0, 'vol_multiplier': 3.0},
                'correlation_breakdown': {'correlation_increase': 0.8},
                'interest_rate_shock': {'return_impact': -0.05},
                'liquidity_crisis': {'return': -0.15, 'vol_multiplier': 1.5}
            }

        base_stats = {
            'mean': returns.mean(),
            'vol': returns.std(),
            'var_95': self.calculate_var(returns, 'historical', 0.95),
            'var_99': self.calculate_var(returns, 'historical', 0.99),
            'cvar_95': self.calculate_cvar(returns, confidence_level=0.95),
            'cvar_99': self.calculate_cvar(returns, confidence_level=0.99)
        }

        stress_results = {'base_scenario': base_stats}

        for scenario_name, scenario_params in stress_scenarios.items():
            if 'return' in scenario_params:
                # Apply return shock
                stressed_returns = returns + scenario_params['return']
            else:
                stressed_returns = returns.copy()

            if 'vol_multiplier' in scenario_params:
                # Increase volatility
                stressed_returns = stressed_returns * scenario_params['vol_multiplier']

            # Calculate stressed metrics
            stressed_stats = {
                'mean': stressed_returns.mean(),
                'vol': stressed_returns.std(),
                'var_95': self.calculate_var(stressed_returns, 'historical', 0.95),
                'var_99': self.calculate_var(stressed_returns, 'historical', 0.99),
                'cvar_95': self.calculate_cvar(stressed_returns, confidence_level=0.95),
                'cvar_99': self.calculate_cvar(stressed_returns, confidence_level=0.99)
            }

            stress_results[scenario_name] = stressed_stats

        return stress_results

    def portfolio_risk_contribution(self, returns: pd.DataFrame, weights: np.array) -> dict:
        """
        Calculate risk contribution of each asset in portfolio

        Args:
            returns (pd.DataFrame): Asset returns
            weights (np.array): Portfolio weights

        Returns:
            dict: Risk contribution analysis
        """
        # Portfolio metrics
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(returns.cov(), weights)))

        # Marginal contribution to risk
        marginal_contrib = np.dot(returns.cov(), weights) / portfolio_vol

        # Component contribution to risk
        component_contrib = weights * marginal_contrib

        # Percentage contribution
        percent_contrib = component_contrib / portfolio_vol

        return {
            'portfolio_volatility': portfolio_vol,
            'marginal_contribution': marginal_contrib,
            'component_contribution': component_contrib,
            'percentage_contribution': percent_contrib,
            'asset_names': returns.columns.tolist()
        }

    def calculate_risk_budget(self, returns: pd.DataFrame, risk_budget: np.array) -> np.array:
        """
        Calculate optimal weights based on risk budget

        Args:
            returns (pd.DataFrame): Asset returns
            risk_budget (np.array): Desired risk contribution percentages

        Returns:
            np.array: Optimal weights
        """
        def risk_budget_objective(weights):
            # Calculate portfolio volatility
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(returns.cov(), weights)))

            # Calculate risk contributions
            marginal_contrib = np.dot(returns.cov(), weights) / portfolio_vol
            component_contrib = weights * marginal_contrib
            percent_contrib = component_contrib / portfolio_vol

            # Objective: minimize squared difference from risk budget
            return np.sum((percent_contrib - risk_budget) ** 2)

        # Constraints
        num_assets = len(returns.columns)
        constraints = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]  # Weights sum to 1
        bounds = tuple((0, 1) for _ in range(num_assets))  # No short selling

        # Initial guess
        initial_weights = np.array([1/num_assets] * num_assets)

        # Optimize
        result = minimize(risk_budget_objective, initial_weights, method='SLSQP',
                         bounds=bounds, constraints=constraints)

        if result.success:
            return result.x
        else:
            raise ValueError("Risk budget optimization failed")

    def correlation_analysis(self, returns: pd.DataFrame, window: int = 60) -> dict:
        """
        Analyze correlation dynamics

        Args:
            returns (pd.DataFrame): Asset returns
            window (int): Rolling window for correlation

        Returns:
            dict: Correlation analysis results
        """
        # Static correlation matrix
        static_corr = returns.corr()

        # Rolling correlation statistics
        rolling_corrs = []
        for i in range(window, len(returns)):
            window_corr = returns.iloc[i-window:i].corr()
            rolling_corrs.append(window_corr.values[np.triu_indices(len(window_corr), 1)])

        rolling_corrs = np.array(rolling_corrs)

        # Correlation statistics
        avg_correlation = np.mean(rolling_corrs)
        correlation_volatility = np.std(rolling_corrs)
        max_correlation = np.max(rolling_corrs)
        min_correlation = np.min(rolling_corrs)

        # Correlation breakdown detection
        recent_corr = rolling_corrs[-1]
        historical_avg = np.mean(rolling_corrs[:-1]) if len(rolling_corrs) > 1 else avg_correlation
        correlation_spike = (recent_corr - historical_avg) / historical_avg

        return {
            'static_correlation': static_corr,
            'rolling_average_correlation': avg_correlation,
            'correlation_volatility': correlation_volatility,
            'max_correlation': max_correlation,
            'min_correlation': min_correlation,
            'correlation_spike': correlation_spike,
            'recent_correlation': recent_corr,
            'historical_correlation_avg': historical_avg
        }

    def position_sizing(self, volatility: np.array, max_portfolio_vol: float = 0.15, max_position_size: float = 0.3) -> np.array:
        """
        Calculate optimal position sizes based on volatility

        Args:
            volatility (np.array): Asset volatilities
            max_portfolio_vol (float): Maximum portfolio volatility
            max_position_size (float): Maximum position size per asset

        Returns:
            np.array: Position sizes
        """
        # Equal risk contribution sizing
        inv_vol = 1 / volatility
        raw_weights = inv_vol / np.sum(inv_vol)

        # Scale to target volatility
        portfolio_vol = np.sqrt(np.sum((raw_weights * volatility) ** 2))
        scaled_weights = raw_weights * (max_portfolio_vol / portfolio_vol)

        # Apply position size limits
        capped_weights = np.minimum(scaled_weights, max_position_size)

        # Renormalize to ensure weights sum to 1
        if np.sum(capped_weights) > 0:
            final_weights = capped_weights / np.sum(capped_weights)
        else:
            final_weights = raw_weights

        return final_weights

    def generate_risk_report(self, returns: pd.Series, benchmark_returns: pd.Series = None, weights: np.array = None) -> dict:
        """
        Generate comprehensive risk report

        Args:
            returns (pd.Series or pd.DataFrame): Portfolio or asset returns
            benchmark_returns (pd.Series): Benchmark returns
            weights (np.array): Portfolio weights (for multi-asset portfolios)

        Returns:
            dict: Comprehensive risk report
        """
        report = {}

        # Basic statistics
        report['basic_stats'] = {
            'mean': returns.mean(),
            'std': returns.std(),
            'skewness': stats.skew(returns),
            'kurtosis': stats.kurtosis(returns),
            'min': returns.min(),
            'max': returns.max()
        }

        # VaR and CVaR
        report['var_analysis'] = {
            'var_95_historical': self.calculate_var(returns, 'historical', 0.95),
            'var_99_historical': self.calculate_var(returns, 'historical', 0.99),
            'var_95_parametric': self.calculate_var(returns, 'parametric', 0.95),
            'var_99_parametric': self.calculate_var(returns, 'parametric', 0.99),
            'cvar_95': self.calculate_cvar(returns, confidence_level=0.95),
            'cvar_99': self.calculate_cvar(returns, confidence_level=0.99)
        }

        # Drawdown analysis
        if isinstance(returns, pd.Series) and returns.min() < 0:
            cumulative = (1 + returns).cumprod()
        else:
            cumulative = returns
        report['drawdown_analysis'] = self.calculate_drawdown_metrics(cumulative, is_returns=False)

        # Risk-adjusted metrics
        report['risk_adjusted_metrics'] = self.calculate_risk_adjusted_metrics(
            returns, benchmark_returns)

        # Portfolio-specific analysis
        if isinstance(returns, pd.DataFrame) and weights is not None:
            # Risk contribution
            risk_contrib = self.portfolio_risk_contribution(returns, weights)
            report['risk_contribution'] = risk_contrib

            # Correlation analysis
            corr_analysis = self.correlation_analysis(returns)
            report['correlation_analysis'] = corr_analysis

        # Stress testing
        stress_results = self.stress_testing(returns)
        report['stress_testing'] = stress_results

        return report

    def plot_risk_metrics(self, risk_report: dict):
        """
        Plot risk metrics from risk report
        """
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))

        # VaR Comparison
        var_data = risk_report['var_analysis']
        methods = ['Historical 95%', 'Historical 99%', 'Parametric 95%', 'Parametric 99%']
        values = [var_data['var_95_historical'], var_data['var_99_historical'],
                 var_data['var_95_parametric'], var_data['var_99_parametric']]

        axes[0, 0].bar(methods, values)
        axes[0, 0].set_title('Value at Risk Comparison')
        axes[0, 0].tick_params(axis='x', rotation=45)

        # CVaR Comparison
        cvar_values = [var_data['cvar_95'], var_data['cvar_99']]
        cvar_labels = ['CVaR 95%', 'CVaR 99%']
        axes[0, 1].bar(cvar_labels, cvar_values)
        axes[0, 1].set_title('Conditional Value at Risk')

        # Drawdown Analysis
        dd_data = risk_report['drawdown_analysis']
        dd_metrics = ['Max DD', 'Avg DD']
        dd_values = [dd_data['max_drawdown'], dd_data['avg_drawdown']]
        axes[0, 2].bar(dd_metrics, dd_values)
        axes[0, 2].set_title('Drawdown Metrics')
        axes[0, 2].tick_params(axis='x', rotation=45)

        # Risk-Adjusted Metrics
        risk_adj = risk_report['risk_adjusted_metrics']
        metrics_names = ['Sharpe', 'Sortino', 'Calmar', 'Information', 'Treynor']
        metrics_values = [risk_adj['sharpe_ratio'], risk_adj['sortino_ratio'],
                         risk_adj['calmar_ratio'], risk_adj['information_ratio'],
                         risk_adj['treynor_ratio']]

        axes[1, 0].bar(metrics_names, metrics_values)
        axes[1, 0].set_title('Risk-Adjusted Performance Metrics')
        axes[1, 0].tick_params(axis='x', rotation=45)

        # Stress Testing Results
        stress_results = risk_report['stress_testing']
        scenarios = list(stress_results.keys())[1:]  # Exclude base scenario
        var_95_stress = [stress_results[s]['var_95'] for s in scenarios]

        axes[1, 1].bar(scenarios, var_95_stress)
        axes[1, 1].set_title('Stress Test - 95% VaR')
        axes[1, 1].tick_params(axis='x', rotation=45)

        # Basic Statistics
        basic_stats = risk_report['basic_stats']
        stat_names = ['Mean', 'Std', 'Skewness', 'Kurtosis', 'Min', 'Max']
        stat_values = [basic_stats['mean'], basic_stats['std'], basic_stats['skewness'],
                      basic_stats['kurtosis'], basic_stats['min'], basic_stats['max']]

        axes[1, 2].bar(stat_names, stat_values)
        axes[1, 2].set_title('Basic Return Statistics')
        axes[1, 2].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.show()


def main():
    parser = argparse.ArgumentParser(description='Risk management and analysis tools')
    parser.add_argument('--ticker', '-t', type=str, help='Single ticker for analysis')
    parser.add_argument('--tickers', type=str, help='Comma-separated tickers for portfolio analysis')
    parser.add_argument('--period', type=str, default='2y', help='Analysis period')
    parser.add_argument('--weights', type=str, help='Portfolio weights (comma-separated)')
    parser.add_argument('--benchmark', type=str, help='Benchmark ticker')
    parser.add_argument('--confidence', type=float, default=0.95, help='Confidence level for VaR')
    parser.add_argument('--var-method', choices=['historical', 'parametric', 'monte_carlo'], default='historical', help='VaR calculation method')
    parser.add_argument('--stress-test', action='store_true', help='Run stress testing')
    parser.add_argument('--risk-report', action='store_true', help='Generate comprehensive risk report')
    parser.add_argument('--plot', action='store_true', help='Plot risk metrics')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Initialize risk manager
    risk_manager = RiskManager(args.confidence)

    try:
        if args.ticker:
            # Single asset analysis
            print(f"Analyzing risk for {args.ticker}...")
            fetcher = DataFetcher()
            data = fetcher.fetch_stock_data(args.ticker, period=args.period)

            if data is None:
                print(f"Could not fetch data for {args.ticker}")
                return

            returns = data['Returns'].dropna()

            # Benchmark data
            benchmark_returns = None
            if args.benchmark:
                benchmark_data = fetcher.fetch_stock_data(args.benchmark, period=args.period)
                if benchmark_data is not None:
                    benchmark_returns = benchmark_data['Returns'].dropna()

            # VaR calculation
            var = risk_manager.calculate_var(returns, args.var_method, args.confidence)
            cvar = risk_manager.calculate_cvar(returns, var, args.confidence)

            print(f"\nValue at Risk ({args.confidence*100:.0f}% confidence): {var:.4f} ({var*100:.2f}%)")
            print(f"Conditional VaR ({args.confidence*100:.0f}% confidence): {cvar:.4f} ({cvar*100:.2f}%)")

            # Drawdown analysis
            if isinstance(returns, pd.Series) and returns.min() < 0:
                cumulative = (1 + returns).cumprod()
            else:
                cumulative = returns
            drawdown_metrics = risk_manager.calculate_drawdown_metrics(cumulative, is_returns=False)

            print(f"\nDrawdown Analysis:")
            print(f"Maximum Drawdown: {drawdown_metrics['max_drawdown']:.4f} ({drawdown_metrics['max_drawdown']*100:.2f}%)")
            print(f"Average Drawdown: {drawdown_metrics['avg_drawdown']:.4f} ({drawdown_metrics['avg_drawdown']*100:.2f}%)")
            print(f"Max Drawdown Duration: {drawdown_metrics['max_drawdown_duration']} days")
            print(f"Current Drawdown: {drawdown_metrics['current_drawdown']:.4f} ({drawdown_metrics['current_drawdown']*100:.2f}%)")

            # Risk-adjusted metrics
            risk_adj_metrics = risk_manager.calculate_risk_adjusted_metrics(returns, benchmark_returns)

            print(f"\nRisk-Adjusted Metrics:")
            print(f"Sharpe Ratio: {risk_adj_metrics['sharpe_ratio']:.3f}")
            print(f"Sortino Ratio: {risk_adj_metrics['sortino_ratio']:.3f}")
            print(f"Calmar Ratio: {risk_adj_metrics['calmar_ratio']:.3f}")
            if benchmark_returns is not None:
                print(f"Information Ratio: {risk_adj_metrics['information_ratio']:.3f}")
                print(f"Treynor Ratio: {risk_adj_metrics['treynor_ratio']:.3f}")
                print(f"Beta: {risk_adj_metrics['beta']:.3f}")

            # Stress testing
            if args.stress_test:
                print(f"\nRunning Stress Testing...")
                stress_results = risk_manager.stress_testing(returns)

                for scenario, metrics in stress_results.items():
                    print(f"\n{scenario.replace('_', ' ').title()} Scenario:")
                    print(f"  95% VaR: {metrics['var_95']:.4f} ({metrics['var_95']*100:.2f}%)")
                    print(f"  99% VaR: {metrics['var_99']:.4f} ({metrics['var_99']*100:.2f}%)")
                    print(f"  95% CVaR: {metrics['cvar_95']:.4f} ({metrics['cvar_95']*100:.2f}%)")

            # Comprehensive risk report
            if args.risk_report:
                print(f"\nGenerating Comprehensive Risk Report...")
                risk_report = risk_manager.generate_risk_report(returns, benchmark_returns)

                if args.output:
                    # Save report to file
                    import json
                    with open(args.output, 'w') as f:
                        json.dump(risk_report, f, indent=2, default=str)
                    print(f"Risk report saved to {args.output}")

                if args.plot:
                    risk_manager.plot_risk_metrics(risk_report)

        elif args.tickers:
            # Portfolio analysis
            tickers = [t.strip() for t in args.tickers.split(',')]
            weights = None

            if args.weights:
                weights = [float(w.strip()) for w in args.weights.split(',')]
                if len(weights) != len(tickers):
                    print("Number of weights must match number of tickers")
                    return
                weights = np.array(weights)
                weights = weights / np.sum(weights)  # Normalize

            print(f"Analyzing portfolio risk for {len(tickers)} assets...")
            fetcher = DataFetcher()

            # Fetch data for all assets
            portfolio_data = {}
            for ticker in tickers:
                data = fetcher.fetch_stock_data(ticker, period=args.period)
                if data is not None:
                    portfolio_data[ticker] = data['Returns'].dropna()

            if len(portfolio_data) < 2:
                print("Could not fetch sufficient data for portfolio analysis")
                return

            returns_df = pd.DataFrame(portfolio_data).dropna()

            if weights is None:
                weights = np.array([1/len(tickers)] * len(tickers))

            # Portfolio returns
            portfolio_returns = (returns_df * weights).sum(axis=1)

            print(f"\nPortfolio Risk Analysis:")

            # Portfolio VaR and CVaR
            portfolio_var = risk_manager.calculate_var(portfolio_returns, args.var_method, args.confidence)
            portfolio_cvar = risk_manager.calculate_cvar(portfolio_returns, portfolio_var, args.confidence)

            print(f"Portfolio VaR ({args.confidence*100:.0f}%): {portfolio_var:.4f} ({portfolio_var*100:.2f}%)")
            print(f"Portfolio CVaR ({args.confidence*100:.0f}%): {portfolio_cvar:.4f} ({portfolio_cvar*100:.2f}%)")

            # Risk contribution analysis
            risk_contrib = risk_manager.portfolio_risk_contribution(returns_df, weights)

            print(f"\nRisk Contribution Analysis:")
            for i, (ticker, contrib) in enumerate(zip(tickers, risk_contrib['percentage_contribution'])):
                print(f"{ticker}: {contrib:.2%}")

            # Correlation analysis
            corr_analysis = risk_manager.correlation_analysis(returns_df)

            print(f"\nCorrelation Analysis:")
            print(f"Average Correlation: {corr_analysis['rolling_average_correlation']:.3f}")
            print(f"Correlation Volatility: {corr_analysis['correlation_volatility']:.3f}")
            print(f"Recent Correlation Spike: {corr_analysis['correlation_spike']:.2%}")

        else:
            print("Please specify either --ticker or --tickers for analysis")
            return

    except Exception as e:
        print(f"Error during risk analysis: {e}")


if __name__ == "__main__":
    main()

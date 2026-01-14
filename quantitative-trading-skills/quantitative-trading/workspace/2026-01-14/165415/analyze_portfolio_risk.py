#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Add skill path to sys.path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import DataFetcher, RiskManager, PortfolioAnalyzer

# Configuration
now = datetime.now()
output_dir = f"/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading/workspace/{now.strftime('%Y-%m-%d')}/{now.strftime('%H%M%S')}"
os.makedirs(output_dir, exist_ok=True)

# Portfolio Data (Extracted from image)
CASH = 74915.92
MARKET_VALUE_TOTAL = 19460.60
TOTAL_ASSETS = CASH + MARKET_VALUE_TOTAL

portfolio_holdings = {
    '510150.SH': 2875.00,  # 消费 ETF
    '510880.SH': 3229.00,  # 红利 ETF
    '513180.SH': 617.60,   # 恒指科技
    '513630.SH': 812.00,   # 香港红利
    '515050.SH': 2301.00,  # 5GETF
    '515070.SH': 838.40,   # AI智能
    '588000.SH': 3098.00,  # 科创 50
    '159770.SZ': 781.20,   # 机器人 AI
    '159830.SZ': 4084.00,  # 上海金
    '161226.SZ': 824.40    # 白银基金
}

tickers = list(portfolio_holdings.keys())
weights_risky = np.array([portfolio_holdings[t] / MARKET_VALUE_TOTAL for t in tickers])

# Initialize
fetcher = DataFetcher()
rm = RiskManager()
pa = PortfolioAnalyzer()

print(f"Fetching data for {len(tickers)} tickers...")
try:
    # Fetch historical data for benchmark (CSI 300)
    benchmark_ticker = '000300.XSHG'
    benchmark_data = fetcher.fetch_stock_data(benchmark_ticker, period='1y')
    benchmark_returns = benchmark_data['Returns'].dropna() if benchmark_data is not None else None

    # Fetch risky asset data
    asset_data = {}
    for t in tickers:
        data = fetcher.fetch_stock_data(t, period='1y')
        if data is not None and not data.empty:
            asset_data[t] = data['Returns']
    
    returns_df = pd.DataFrame(asset_data).dropna()
    common_index = returns_df.index
    
    # Portfolio returns (risky part)
    portfolio_returns_risky = (returns_df * weights_risky).sum(axis=1)
    
    # Portfolio returns (entire portfolio including cash)
    # Cash return is assumed to be 0 for simplicity (daily) or a risk-free rate
    cash_weight = CASH / TOTAL_ASSETS
    risky_weight = MARKET_VALUE_TOTAL / TOTAL_ASSETS
    portfolio_returns_total = portfolio_returns_risky * risky_weight
    
    # Generate Risk Report
    risk_report = rm.generate_risk_report(portfolio_returns_total, benchmark_returns)
    
    # Risk Contribution (Risky part)
    risk_contrib = rm.portfolio_risk_contribution(returns_df, weights_risky)
    
    # Correlation Matrix
    corr_matrix = returns_df.corr()
    
    # Optimization Suggestion (Max Sharpe on Risky Assets)
    opt_result = pa.optimize_portfolio(returns_df, optimization_method='sharpe')
    
    # Efficient Frontier
    ef_result = pa.calculate_efficient_frontier(returns_df)
    
    # Save visualizations
    # 1. Correlation Matrix Heatmap
    plt.figure(figsize=(10, 8))
    import seaborn as sns
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f")
    plt.title('Portfolio Asset Correlation Matrix')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/correlation_matrix.png")
    plt.close()
    
    # 2. Risk Contribution Pie Chart
    plt.figure(figsize=(8, 8))
    plt.pie(risk_contrib['percentage_contribution'], labels=tickers, autopct='%1.1f%%', startangle=140)
    plt.title('Risk Contribution by Asset')
    plt.axis('equal')
    plt.savefig(f"{output_dir}/risk_contribution.png")
    plt.close()

    # 3. Efficient Frontier
    plt.figure(figsize=(10, 6))
    plt.scatter(ef_result['portfolios']['volatility'] * 100, 
                ef_result['portfolios']['return'] * 100, 
                c=ef_result['portfolios']['sharpe_ratio'], cmap='viridis')
    plt.scatter(ef_result['max_sharpe_portfolio']['volatility'] * 100, 
                ef_result['max_sharpe_portfolio']['return'] * 100, 
                color='red', marker='*', s=200, label='Max Sharpe')
    # Current risky portfolio point
    current_vol = portfolio_returns_risky.std() * np.sqrt(252) * 100
    current_ret = portfolio_returns_risky.mean() * 252 * 100
    plt.scatter(current_vol, current_ret, color='black', marker='X', s=200, label='Current Risky Portfolio')
    plt.colorbar(label='Sharpe Ratio')
    plt.xlabel('Volatility (%)')
    plt.ylabel('Expected Return (%)')
    plt.title('Efficient Frontier')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_dir}/efficient_frontier.png")
    plt.close()

    # Consolidate results
    results = {
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        'portfolio_assets': {
            'total_assets': TOTAL_ASSETS,
            'cash': CASH,
            'market_value': MARKET_VALUE_TOTAL,
            'cash_ratio': cash_weight,
            'risky_ratio': risky_weight
        },
        'risk_metrics': risk_report,
        'risk_contribution': {
            'asset_names': risk_contrib['asset_names'],
            'percentage_contribution': risk_contrib['percentage_contribution'].tolist()
        },
        'optimization': {
            'success': opt_result['success'],
            'optimal_weights': opt_result['weights'].tolist() if opt_result['success'] else None,
            'optimal_metrics': opt_result['metrics'] if opt_result['success'] else None
        }
    }
    
    # Handle non-serializable objects in risk_report
    def json_serializable(obj):
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series):
            return {str(k): v for k, v in obj.to_dict().items()}
        if isinstance(obj, pd.DataFrame):
            return {str(k): v for k, v in obj.to_dict().items()}
        if isinstance(obj, (pd.Timestamp, datetime)):
            return obj.isoformat()
        if isinstance(obj, dict):
            return {str(k): json_serializable(v) for k, v in obj.items()}
        if hasattr(obj, 'tolist'):
            return obj.tolist()
        return str(obj)

    # Recursive cleaning function for dictionaries to ensure all keys are strings
    def clean_dict(d):
        if not isinstance(d, dict):
            return json_serializable(d)
        return {str(k): clean_dict(v) for k, v in d.items()}

    results_clean = clean_dict(results)

    with open(f"{output_dir}/analysis_result.json", 'w') as f:
        json.dump(results_clean, f, indent=2)

    print(f"Analysis complete. Results saved to {output_dir}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

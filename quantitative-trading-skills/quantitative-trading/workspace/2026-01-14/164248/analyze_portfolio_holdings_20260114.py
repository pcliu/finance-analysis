#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Add the project root to sys.path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import DataFetcher, PortfolioAnalyzer, RiskManager

def main():
    # 1. Setup output directory
    now = datetime.now()
    output_dir = f"workspace/{now.strftime('%Y-%m-%d')}/{now.strftime('%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    # 2. Define current holdings (based on image)
    holdings = {
        '510150.SH': {'name': '消费 ETF', 'market_value': 2875.00},
        '510880.SH': {'name': '红利 ETF', 'market_value': 3229.00},
        '513180.SH': {'name': '恒指科技', 'market_value': 617.60},
        '513630.SH': {'name': '香港红利', 'market_value': 812.00},
        '515050.SH': {'name': '5GETF', 'market_value': 2301.00},
        '515070.SH': {'name': 'AI 智能', 'market_value': 838.40},
        '588000.SH': {'name': '科创 50', 'market_value': 3098.00},
        '159770.SZ': {'name': '机器人 AI', 'market_value': 781.20},
        '159830.SZ': {'name': '上海金', 'market_value': 4084.00},
        '161226.SZ': {'name': '白银基金', 'market_value': 824.40}
    }
    
    cash = 74915.92
    total_assets = 94376.52
    
    tickers = list(holdings.keys())
    current_market_values = np.array([holdings[t]['market_value'] for t in tickers])
    current_weights = current_market_values / total_assets
    cash_weight = cash / total_assets
    
    print(f"Total Assets: {total_assets}")
    print(f"Cash Weight: {cash_weight:.2%}")
    
    # 3. Fetch data
    pa = PortfolioAnalyzer()
    print("Fetching historical data...")
    price_data = pa.create_portfolio_data(tickers, period='1y')
    
    if price_data is None:
        print("Error: Could not fetch price data.")
        return
        
    returns = pa.calculate_returns(price_data)
    
    # 4. Analyze current portfolio
    # (Note: Current weight sum to ~20.6%, we need to account for cash if we want total portfolio metrics)
    # However, PortfolioAnalyzer.calculate_portfolio_metrics expects weights to sum to 1.
    # We can add a 'CASH' asset with 0 return and 0 volatility.
    
    returns_with_cash = returns.copy()
    returns_with_cash['CASH'] = 0.0
    
    all_tickers = tickers + ['CASH']
    all_current_weights = np.append(current_weights, cash_weight)
    
    current_metrics = pa.calculate_portfolio_metrics(returns_with_cash, all_current_weights)
    
    # 5. Optimization
    # We'll optimize the risky assets part (the 10 ETFs) and also suggest re-allocation including cash
    # Optimization method: Max Sharpe
    print("Optimizing portfolio (Max Sharpe)...")
    opt_result = pa.optimize_portfolio(returns, optimization_method='sharpe')
    
    # Optimization with cash (Targeting a higher return by utilizing cash)
    # For simplicity, let's optimize the 10 ETFs first.
    
    # 6. Efficient Frontier
    print("Calculating efficient frontier...")
    ef_results = pa.calculate_efficient_frontier(returns, num_portfolios=500)
    
    # 7. Correlation Analysis
    correlation_matrix = returns.corr()
    
    # 8. Save results
    # 8. Save results
    def safe_json_serialize(obj):
        if isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, pd.Series):
            return obj.tolist()
        return obj

    analysis_result = {
        'timestamp': now.strftime('%Y-%m-%d %H:%M:%S'),
        'current_portfolio': {
            'metrics': {k: safe_json_serialize(v) for k, v in current_metrics.items() if k != 'portfolio_returns'},
            'weights': {t: float(w) for t, w in zip(all_tickers, all_current_weights)}
        },
        'optimization': {
            'max_sharpe': {
                'weights': {t: float(w) for t, w in zip(opt_result['asset_names'], opt_result['weights'])},
                'metrics': {k: safe_json_serialize(v) for k, v in opt_result['metrics'].items() if k != 'portfolio_returns'}
            }
        },
        'correlation': correlation_matrix.to_dict()
    }

    with open(f"{output_dir}/analysis_result.json", 'w') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
        
    # 9. Plotting
    plt.figure(figsize=(12, 8))
    plt.scatter(ef_results['portfolios']['volatility'] * 100, 
                ef_results['portfolios']['return'] * 100, 
                c=ef_results['portfolios']['sharpe_ratio'], cmap='viridis', alpha=0.5)
    plt.colorbar(label='Sharpe Ratio')
    
    # Mark Max Sharpe Portfolio
    plt.scatter(opt_result['metrics']['volatility'] * 100, 
                opt_result['metrics']['expected_return'] * 100, 
                color='red', marker='*', s=200, label='Max Sharpe (ETF only)')
    
    # Mark Current Portfolio (Risky assets only, normalized)
    risky_returns = returns
    risky_current_weights = current_market_values / current_market_values.sum()
    risky_metrics = pa.calculate_portfolio_metrics(risky_returns, risky_current_weights)
    plt.scatter(risky_metrics['volatility'] * 100, 
                risky_metrics['expected_return'] * 100, 
                color='blue', marker='o', s=100, label='Current Portfolio (Risky part)')
    
    plt.xlabel('Annualized Volatility (%)')
    plt.ylabel('Annualized Expected Return (%)')
    plt.title('Portfolio Optimization: Efficient Frontier')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/efficient_frontier.png")
    
    # Correlation Heatmap
    plt.figure(figsize=(10, 8))
    import seaborn as sns
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Asset Correlation Matrix')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/correlation_matrix.png")
    
    print(f"Analysis complete. Results saved to {output_dir}/")

if __name__ == "__main__":
    main()

"""
Compare multiple stocks and save comparison results.

Usage:
    from skills.compare_stocks import compare_stocks
    
    result = compare_stocks(['AAPL', 'GOOGL', 'MSFT'], period='1y')
    # Results saved to workspace/comparison_AAPL_GOOGL_MSFT.json
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.data_fetcher import fetch_multiple_stocks, get_data_summary
from api.risk import calculate_max_drawdown

WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), '..', 'workspace')
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def compare_stocks(tickers: list, period: str = '1y'):
    """
    Compare multiple stocks and save results.
    
    Args:
        tickers: List of ticker symbols
        period: Analysis period
    
    Returns:
        dict: Comparison summary
    
    Example:
        result = compare_stocks(['AAPL', 'GOOGL'], period='6mo')
        print(f"Best performer: {result['best_performer']}")
    """
    # Fetch data for all stocks
    data_dict = fetch_multiple_stocks(tickers, period=period)
    
    comparison = {
        'tickers': tickers,
        'timestamp': datetime.now().isoformat(),
        'period': period,
        'stocks': {}
    }
    
    # Analyze each stock
    for ticker in tickers:
        if ticker not in data_dict:
            continue
        
        data = data_dict[ticker]
        returns = data['Returns'].dropna()
        summary = get_data_summary(ticker, period)
        drawdown = calculate_max_drawdown(returns)
        
        # Extract key metrics only
        comparison['stocks'][ticker] = {
            'current_price': float(data['Close'].iloc[-1]),
            'total_return': summary.get('Total Return (%)', 0),
            'volatility': summary.get('Annualized Volatility (%)', 0),
            'sharpe_ratio': summary.get('Sharpe Ratio', 0),
            'max_drawdown': float(drawdown['max_drawdown']),
        }
    
    # Find best performer
    if comparison['stocks']:
        best = max(comparison['stocks'].items(), key=lambda x: x[1]['total_return'])
        comparison['best_performer'] = best[0]
        comparison['best_return'] = best[1]['total_return']
    
    # Save to workspace
    filename = f"comparison_{'_'.join(tickers)}.json"
    file_path = os.path.join(WORKSPACE_DIR, filename)
    with open(file_path, 'w') as f:
        json.dump(comparison, f, indent=2)
    
    return {
        'file_path': file_path,
        'best_performer': comparison.get('best_performer'),
        'summary': {t: s['total_return'] for t, s in comparison['stocks'].items()}
    }


async def compare_stocks_async(tickers: list, period: str = '1y'):
    """Async wrapper for convenience."""
    return compare_stocks(tickers, period)

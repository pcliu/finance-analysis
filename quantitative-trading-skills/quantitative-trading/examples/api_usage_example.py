#!/usr/bin/env python3
"""
API Usage Example - Demonstrating Code Execution Pattern

This example shows how to use the API in a context-efficient way:
1. Import only needed functions
2. Filter and transform data before returning to model
3. Save intermediate results to workspace
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Progressive discovery: Import only what you need
from api.data_fetcher import fetch_stock_data, get_company_info
from api.indicators import calculate_rsi, calculate_sma, calculate_macd
from api.strategies import moving_average_crossover
from api.backtester import backtest_strategy

def analyze_stock_efficiently(ticker: str, period: str = '1y'):
    """
    Example of context-efficient analysis.
    Only returns summary, not full datasets.
    """
    print(f"Analyzing {ticker}...")
    
    # Fetch data
    data = fetch_stock_data(ticker, period=period)
    if data is None:
        return None
    
    # Filter to recent data only (context efficient)
    recent_data = data.tail(60)  # Last 60 days
    
    # Calculate indicators
    rsi = calculate_rsi(recent_data)
    sma_20 = calculate_sma(recent_data, window=20)
    macd = calculate_macd(recent_data)
    
    # Extract only latest values (not full series)
    summary = {
        'ticker': ticker,
        'current_price': float(recent_data['Close'].iloc[-1]),
        'rsi': float(rsi.iloc[-1]),
        'sma_20': float(sma_20.iloc[-1]),
        'macd': float(macd['MACD'].iloc[-1]),
        'macd_signal': float(macd['Signal'].iloc[-1]),
    }
    
    # Generate signals
    signals = moving_average_crossover(recent_data, fast_window=20, slow_window=50)
    buy_signals = signals[signals['Buy_Signal'] == True]
    sell_signals = signals[signals['Sell_Signal'] == True]
    
    summary['signals'] = {
        'buy_count': len(buy_signals),
        'sell_count': len(sell_signals),
        'latest_buy': buy_signals.index[-1].isoformat() if len(buy_signals) > 0 else None,
        'latest_sell': sell_signals.index[-1].isoformat() if len(sell_signals) > 0 else None,
    }
    
    return summary

def backtest_with_summary(ticker: str, strategy: str = 'moving_average_crossover'):
    """
    Example of backtesting with summary output.
    """
    print(f"Backtesting {strategy} for {ticker}...")
    
    # Fetch longer period for backtesting
    data = fetch_stock_data(ticker, period='2y')
    if data is None:
        return None
    
    # Run backtest
    results = backtest_strategy(data, strategy, {
        'fast_window': 20,
        'slow_window': 50
    })
    
    # Return only key metrics (not full trade log)
    summary = {
        'ticker': ticker,
        'strategy': strategy,
        'total_return': results.get('total_return', 0),
        'sharpe_ratio': results.get('sharpe_ratio', 0),
        'max_drawdown': results.get('max_drawdown', 0),
        'win_rate': results.get('win_rate', 0),
        'total_trades': results.get('total_trades', 0),
    }
    
    return summary

def compare_multiple_stocks_efficiently(tickers: list):
    """
    Example of comparing multiple stocks efficiently.
    Only returns summary statistics.
    """
    print(f"Comparing {len(tickers)} stocks...")
    
    from api.data_fetcher import fetch_multiple_stocks, get_data_summary
    
    # Fetch all data
    data_dict = fetch_multiple_stocks(tickers, period='1y')
    
    # Process each stock and extract only summaries
    comparison = {}
    for ticker in tickers:
        if ticker not in data_dict:
            continue
        
        summary = get_data_summary(ticker, period='1y')
        comparison[ticker] = {
            'current_price': summary.get('Current Price', 0),
            'total_return': summary.get('Total Return (%)', 0),
            'volatility': summary.get('Annualized Volatility (%)', 0),
            'sharpe_ratio': summary.get('Sharpe Ratio', 0),
        }
    
    # Find best performer
    if comparison:
        best = max(comparison.items(), key=lambda x: x[1]['total_return'])
        comparison['_best_performer'] = best[0]
    
    return comparison

if __name__ == "__main__":
    # Example 1: Single stock analysis
    print("=" * 50)
    print("Example 1: Single Stock Analysis")
    print("=" * 50)
    result = analyze_stock_efficiently('AAPL', period='6mo')
    if result:
        print(f"\nSummary for {result['ticker']}:")
        print(f"  Price: ${result['current_price']:.2f}")
        print(f"  RSI: {result['rsi']:.2f}")
        print(f"  Buy signals: {result['signals']['buy_count']}")
        print(f"  Sell signals: {result['signals']['sell_count']}")
    
    # Example 2: Backtesting
    print("\n" + "=" * 50)
    print("Example 2: Strategy Backtesting")
    print("=" * 50)
    backtest_result = backtest_with_summary('AAPL')
    if backtest_result:
        print(f"\nBacktest Results:")
        print(f"  Total Return: {backtest_result['total_return']:.2f}%")
        print(f"  Sharpe Ratio: {backtest_result['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {backtest_result['max_drawdown']:.2f}%")
        print(f"  Win Rate: {backtest_result['win_rate']:.2f}%")
    
    # Example 3: Stock comparison
    print("\n" + "=" * 50)
    print("Example 3: Stock Comparison")
    print("=" * 50)
    comparison = compare_multiple_stocks_efficiently(['AAPL', 'GOOGL', 'MSFT'])
    if comparison:
        print(f"\nComparison Results:")
        for ticker, metrics in comparison.items():
            if ticker.startswith('_'):
                continue
            print(f"\n{ticker}:")
            print(f"  Return: {metrics['total_return']:.2f}%")
            print(f"  Sharpe: {metrics['sharpe_ratio']:.2f}")
        if '_best_performer' in comparison:
            print(f"\nBest Performer: {comparison['_best_performer']}")

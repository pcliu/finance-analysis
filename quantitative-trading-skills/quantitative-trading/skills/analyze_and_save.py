"""
Analyze a stock and save results to workspace.

This is a reusable skill that can be saved and reused across sessions.

Usage:
    from skills.analyze_and_save import analyze_and_save
    
    result = analyze_and_save('AAPL', period='1y')
    # Results saved to workspace/analysis_AAPL.json
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.data_fetcher import fetch_stock_data, get_company_info
from api.indicators import calculate_rsi, calculate_sma, calculate_macd
from api.risk import calculate_max_drawdown

# Ensure workspace directory exists
WORKSPACE_DIR = os.path.join(os.path.dirname(__file__), '..', 'workspace')
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def analyze_and_save(ticker: str, period: str = '1y'):
    """Analyze a stock and save results to workspace."""
    data = fetch_stock_data(ticker, period=period)
    if data is None:
        return {'error': f'Could not fetch data for {ticker}'}

    company_info = get_company_info(ticker)

    # Calculate indicators
    rsi = calculate_rsi(data)
    sma_20 = calculate_sma(data, window=20)
    sma_50 = calculate_sma(data, window=50)
    macd = calculate_macd(data)

    # Calculate returns and risk metrics
    returns = data['Returns'].dropna()
    drawdown_metrics = calculate_max_drawdown(returns)

    # Extract only latest values (context efficient)
    current_price = data['Close'].iloc[-1]
    current_rsi = rsi.iloc[-1]
    current_sma_20 = sma_20.iloc[-1]
    current_sma_50 = sma_50.iloc[-1]
    current_macd = macd['MACD'].iloc[-1]
    current_signal = macd['Signal'].iloc[-1]

    analysis = {
        'ticker': ticker,
        'timestamp': datetime.now().isoformat(),
        'company': {
            'name': company_info.get('Name', 'N/A'),
            'sector': company_info.get('Sector', 'N/A'),
            'industry': company_info.get('Industry', 'N/A'),
        },
        'price': {
            'current': float(current_price),
            'period_high': float(data['High'].max()),
            'period_low': float(data['Low'].min()),
            'total_return': float((current_price / data['Close'].iloc[0] - 1) * 100),
        },
        'indicators': {
            'rsi': float(current_rsi),
            'sma_20': float(current_sma_20),
            'sma_50': float(current_sma_50),
            'macd': float(current_macd),
            'macd_signal': float(current_signal),
        },
        'risk': {
            'max_drawdown': float(drawdown_metrics['max_drawdown']),
            'volatility': float(data['Volatility'].iloc[-1]),
        },
        'signals': {
            'trend': 'bullish' if current_price > current_sma_20 > current_sma_50 else 'bearish' if current_price < current_sma_20 < current_sma_50 else 'neutral',
            'rsi_signal': 'overbought' if current_rsi > 70 else 'oversold' if current_rsi < 30 else 'neutral',
        }
    }

    file_path = os.path.join(WORKSPACE_DIR, f'analysis_{ticker}.json')
    with open(file_path, 'w') as f:
        json.dump(analysis, f, indent=2)

    return {
        'ticker': ticker,
        'file_path': file_path,
        'summary': {
            'price': analysis['price']['current'],
            'return': analysis['price']['total_return'],
            'trend': analysis['signals']['trend'],
            'rsi_signal': analysis['signals']['rsi_signal'],
        }
    }

async def analyze_and_save_async(ticker: str, period: str = '1y'):
    """
    Analyze a stock and save results to workspace.

    Args:
        ticker: Stock ticker symbol
        period: Analysis period

    Returns:
        dict: Analysis summary

    Example:
        result = await analyze_and_save_async('AAPL')
        print(f"Analysis saved: {result['file_path']}")
    """
    return analyze_and_save(ticker, period)

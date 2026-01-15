#!/usr/bin/env python3
"""
Basic Stock Analysis Example
Demonstrates fundamental data fetching and analysis capabilities
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from data_fetcher import DataFetcher
from indicators import TechnicalIndicators
import matplotlib.pyplot as plt

def analyze_stock(ticker, period='1y'):
    """
    Perform basic stock analysis
    """
    print(f"Analyzing {ticker} over {period} period...")
    print("=" * 50)

    # Initialize components
    fetcher = DataFetcher()
    indicators = TechnicalIndicators()

    # Fetch stock data
    data = fetcher.fetch_stock_data(ticker, period=period)

    if data is None:
        print(f"Could not fetch data for {ticker}")
        return

    # Get company information
    company_info = fetcher.get_company_info(ticker)

    # Calculate basic metrics
    current_price = data['Close'][-1]
    period_high = data['High'].max()
    period_low = data['Low'].min()
    total_return = (data['Close'][-1] / data['Close'][0] - 1) * 100

    # Calculate technical indicators
    sma_20 = indicators.calculate_sma(data, 20)
    sma_50 = indicators.calculate_sma(data, 50)
    rsi = indicators.calculate_rsi(data)

    # Display results
    print(f"\n📊 {ticker} Stock Analysis")
    print(f"Company: {company_info.get('Name', 'N/A')}")
    print(f"Sector: {company_info.get('Sector', 'N/A')}")
    print(f"Industry: {company_info.get('Industry', 'N/A')}")
    print(f"Market Cap: {company_info.get('Market Cap', 'N/A')}")
    print(f"P/E Ratio: {company_info.get('P/E Ratio', 'N/A')}")
    print(f"Beta: {company_info.get('Beta', 'N/A')}")

    print(f"\n💰 Price Information")
    print(f"Current Price: ${current_price:.2f}")
    print(f"Period High: ${period_high:.2f}")
    print(f"Period Low: ${period_low:.2f}")
    print(f"Total Return: {total_return:.2f}%")

    print(f"\n📈 Technical Indicators")
    print(f"SMA 20: ${sma_20.iloc[-1]:.2f}")
    print(f"SMA 50: ${sma_50.iloc[-1]:.2f}")
    print(f"Current RSI: {rsi.iloc[-1]:.2f}")

    # Simple analysis
    print(f"\n🔍 Quick Analysis")

    # Price position vs moving averages
    if current_price > sma_20.iloc[-1] and current_price > sma_50.iloc[-1]:
        trend = "Bullish (above both MAs)"
    elif current_price < sma_20.iloc[-1] and current_price < sma_50.iloc[-1]:
        trend = "Bearish (below both MAs)"
    else:
        trend = "Neutral/Sideways"

    print(f"Trend: {trend}")

    # RSI analysis
    current_rsi = rsi.iloc[-1]
    if current_rsi > 70:
        rsi_signal = "Overbought"
    elif current_rsi < 30:
        rsi_signal = "Oversold"
    else:
        rsi_signal = "Neutral"

    print(f"RSI Signal: {rsi_signal}")

    # Volatility analysis
    volatility = data['Returns'].std() * (252 ** 0.5)  # Annualized
    if volatility > 0.30:
        vol_level = "High"
    elif volatility > 0.20:
        vol_level = "Medium"
    else:
        vol_level = "Low"

    print(f"Volatility: {volatility:.2f} ({vol_level})")

    # Plotting
    try:
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10))

        # Price chart with moving averages
        ax1.plot(data.index, data['Close'], label='Close Price', linewidth=2)
        ax1.plot(data.index, sma_20, label='SMA 20', alpha=0.7)
        ax1.plot(data.index, sma_50, label='SMA 50', alpha=0.7)
        ax1.set_title(f'{ticker} Price Chart')
        ax1.legend()
        ax1.grid(True)

        # Volume chart
        ax2.bar(data.index, data['Volume'], alpha=0.6)
        ax2.set_title('Volume')
        ax2.grid(True)

        # RSI chart
        ax3.plot(data.index, rsi, label='RSI', color='purple')
        ax3.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
        ax3.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
        ax3.set_title('RSI (14)')
        ax3.legend()
        ax3.grid(True)

        plt.tight_layout()
        plt.show()

    except Exception as e:
        print(f"Could not create plots: {e}")

    return data

def main():
    import argparse

    parser = argparse.ArgumentParser(description='Basic stock analysis example')
    parser.add_argument('--ticker', '-t', type=str, required=True, help='Stock ticker symbol')
    parser.add_argument('--period', type=str, default='1y', help='Analysis period')
    parser.add_argument('--plot', action='store_true', help='Show plots')

    args = parser.parse_args()

    try:
        # Only show plots if requested or if running interactively
        if args.plot:
            # This will be handled automatically in the analyze_stock function
            pass
        else:
            # Override matplotlib to not show plots
            import matplotlib
            matplotlib.use('Agg')

        analyze_stock(args.ticker, args.period)

    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user")
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
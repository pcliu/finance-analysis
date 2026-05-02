#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis — 2026-04-29
Covers all 12 current holdings + all ETFs.csv watchlist items.
"""
import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_stochastic, calculate_sma,
    fetch_realtime_quote
)
from scripts.utils import make_serializable

# ── All tickers to analyze ──
# Current holdings (from screenshot)
HOLDINGS = {
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 3.0671, 'market_value': 33250},
    '512170': {'name': '医疗ETF', 'shares': 16000, 'cost': 0.3562, 'market_value': 5440},
    '512660': {'name': '军工ETF', 'shares': 4000, 'cost': 1.6496, 'market_value': 5484},
    '513180': {'name': '恒指科技', 'shares': 4000, 'cost': 0.7479, 'market_value': 2484},
    '515050': {'name': '5GETF', 'shares': 2000, 'cost': 2.1545, 'market_value': 5922},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 1.9388, 'market_value': 874.80},
    '515790': {'name': '光伏ETF', 'shares': 3000, 'cost': 1.1510, 'market_value': 3120},
    '561560': {'name': '电力ETF', 'shares': 2000, 'cost': 1.3623, 'market_value': 2720},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 0.3019, 'market_value': 1568},
    '159516': {'name': '半导体设备', 'shares': 5000, 'cost': 0.9921, 'market_value': 4870},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 0.7670, 'market_value': 208.80},
    '159870': {'name': '化工ETF', 'shares': 7000, 'cost': 0.9071, 'market_value': 6489},
}

# ETFs.csv watchlist (excluding those already in holdings)
WATCHLIST = {
    '510150': {'name': '消费ETF'},
    '159985': {'name': '豆粕ETF'},
    '159689': {'name': '粮食ETF'},
    '561330': {'name': '矿业ETF'},
    '159326': {'name': '电网设备ETF'},
    '560280': {'name': '工程机械ETF'},
    '159241': {'name': '航空航天ETF'},
    '159830': {'name': '上海金ETF'},
    '161226': {'name': '国投白银LOF'},
    '513630': {'name': '港股红利ETF'},
}

ALL_TICKERS = list(HOLDINGS.keys()) + list(WATCHLIST.keys())
ALL_NAMES = {}
for k, v in HOLDINGS.items():
    ALL_NAMES[k] = v['name']
for k, v in WATCHLIST.items():
    ALL_NAMES[k] = v['name']


def analyze_ticker(ticker, name):
    """Run full technical analysis on a single ticker."""
    result = {'ticker': ticker, 'name': name, 'error': None}
    try:
        data = fetch_stock_data(ticker, period='8mo')
        if data is None or len(data) < 30:
            result['error'] = f"Insufficient data: {len(data) if data is not None else 0} rows"
            return result

        # Current price info
        close = data['Close']
        result['latest_price'] = float(close.iloc[-1])
        result['prev_close'] = float(close.iloc[-2])
        result['daily_change_pct'] = float((close.iloc[-1] / close.iloc[-2] - 1) * 100)

        # 5-day and 20-day performance
        if len(close) >= 5:
            result['5d_change_pct'] = float((close.iloc[-1] / close.iloc[-5] - 1) * 100)
        if len(close) >= 20:
            result['20d_change_pct'] = float((close.iloc[-1] / close.iloc[-20] - 1) * 100)

        # RSI
        rsi_df = calculate_rsi(data, window=14)
        result['rsi'] = float(rsi_df['RSI'].iloc[-1])
        if len(rsi_df) >= 6:
            result['rsi_5d_ago'] = float(rsi_df['RSI'].iloc[-5])

        # MACD
        macd_df = calculate_macd(data)
        result['macd'] = float(macd_df['MACD'].iloc[-1])
        result['macd_signal'] = float(macd_df['Signal'].iloc[-1])
        result['macd_hist'] = float(macd_df['Histogram'].iloc[-1])
        # MACD cross detection
        if len(macd_df) >= 2:
            prev_hist = float(macd_df['Histogram'].iloc[-2])
            curr_hist = float(macd_df['Histogram'].iloc[-1])
            if prev_hist < 0 and curr_hist > 0:
                result['macd_cross'] = 'golden_cross'
            elif prev_hist > 0 and curr_hist < 0:
                result['macd_cross'] = 'death_cross'
            else:
                result['macd_cross'] = 'none'

        # Bollinger Bands
        bb_df = calculate_bollinger_bands(data)
        upper = float(bb_df['Upper'].iloc[-1])
        lower = float(bb_df['Lower'].iloc[-1])
        middle = float(bb_df['Middle'].iloc[-1])
        price = float(close.iloc[-1])
        if upper != lower:
            result['bb_pct_b'] = float((price - lower) / (upper - lower))
        else:
            result['bb_pct_b'] = 0.5
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower

        # Stochastic
        stoch_df = calculate_stochastic(data)
        result['stoch_k'] = float(stoch_df['K'].iloc[-1])
        result['stoch_d'] = float(stoch_df['D'].iloc[-1])

        # Volume ratio (current volume / 20-day average)
        if 'Volume' in data.columns:
            vol = data['Volume']
            vol_ma20 = vol.rolling(20).mean()
            if vol_ma20.iloc[-1] > 0:
                result['volume_ratio'] = float(vol.iloc[-1] / vol_ma20.iloc[-1])

        # SMA 5, 20, 60
        sma5 = calculate_sma(data, window=5)['SMA'].iloc[-1]
        sma20 = calculate_sma(data, window=20)['SMA'].iloc[-1]
        sma60 = calculate_sma(data, window=60)['SMA'].iloc[-1] if len(data) >= 60 else None
        result['sma5'] = float(sma5)
        result['sma20'] = float(sma20)
        result['sma60'] = float(sma60) if sma60 is not None else None
        # Trend: price vs SMA
        result['above_sma5'] = price > float(sma5)
        result['above_sma20'] = price > float(sma20)
        if sma60 is not None:
            result['above_sma60'] = price > float(sma60)

    except Exception as e:
        result['error'] = str(e)
    return result


def main():
    print("=" * 60)
    print("Portfolio Technical Analysis — 2026-04-29")
    print("=" * 60)

    all_results = {}

    # Analyze all tickers
    for ticker in ALL_TICKERS:
        name = ALL_NAMES[ticker]
        print(f"\n📊 Analyzing {name} ({ticker})...")
        result = analyze_ticker(ticker, name)
        all_results[ticker] = result

        if result.get('error'):
            print(f"   ⚠️ Error: {result['error']}")
        else:
            rsi_str = f"RSI={result.get('rsi', 'N/A'):.1f}" if result.get('rsi') else "RSI=N/A"
            bb_str = f"%B={result.get('bb_pct_b', 'N/A'):.2f}" if result.get('bb_pct_b') is not None else "%B=N/A"
            hist_str = f"Hist={result.get('macd_hist', 'N/A'):.4f}" if result.get('macd_hist') is not None else "Hist=N/A"
            print(f"   Price={result['latest_price']:.4f} | {rsi_str} | {bb_str} | {hist_str}")

    # Fetch real-time quotes
    print("\n\n📡 Fetching real-time quotes...")
    realtime_data = {}
    try:
        quotes = fetch_realtime_quote(ALL_TICKERS)
        if quotes is not None:
            if hasattr(quotes, 'to_dict'):
                realtime_data = quotes.to_dict('records') if hasattr(quotes, 'to_dict') else {}
            print(f"   ✅ Got {len(realtime_data)} real-time quotes")
    except Exception as e:
        print(f"   ⚠️ Real-time quote error: {e}")

    # Portfolio summary
    print("\n\n" + "=" * 60)
    print("PORTFOLIO SUMMARY")
    print("=" * 60)

    total_assets = 104413.02
    portfolio_mv = 72430.60
    total_pnl = 3533.50
    available = total_assets - portfolio_mv  # 31982.42

    print(f"总资产: ¥{total_assets:,.2f}")
    print(f"持仓市值: ¥{portfolio_mv:,.2f}")
    print(f"可用资金(含货基): ¥{available:,.2f}")
    print(f"持仓盈亏: ¥{total_pnl:+,.2f}")
    print(f"仓位比例: {portfolio_mv/total_assets*100:.1f}%")

    # Save results
    output = {
        'analysis_date': '2026-04-29',
        'portfolio_summary': {
            'total_assets': total_assets,
            'portfolio_mv': portfolio_mv,
            'available_cash': available,
            'total_pnl': total_pnl,
            'position_ratio': round(portfolio_mv / total_assets * 100, 2),
            'today_pnl': 142.30,
        },
        'holdings': HOLDINGS,
        'technical_analysis': all_results,
        'realtime_quotes': realtime_data,
    }

    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(output), f, indent=2, ensure_ascii=False)
    print(f"\n✅ Data saved to {output_path}")

    # Save real-time quotes separately
    rt_path = os.path.join(SCRIPT_DIR, 'realtime_quotes.json')
    with open(rt_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(realtime_data), f, indent=2, ensure_ascii=False)
    print(f"✅ Real-time quotes saved to {rt_path}")


if __name__ == '__main__':
    main()

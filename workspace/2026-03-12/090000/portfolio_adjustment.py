#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis - 2026-03-12
Analyzes all 25 ETFs (11 holdings + 14 watchlist from ETFs.csv)
Data: 2026-03-11 close
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# All tickers: holdings + watchlist from ETFs.csv
ALL_TICKERS = {
    # Current holdings (from screenshot 2026-03-11 close)
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒指科技ETF',
    '515050': '5GETF',
    '515070': 'AI智能ETF',
    '515790': '光伏ETF',
    '588000': '科创50ETF',
    '159241': '航空TH',
    '159770': '机器人AI',
    # Watchlist from ETFs.csv (non-held)
    '159985': '豆粕ETF',
    '512890': '红利低波ETF',
    '159206': '卫星ETF',
    '516780': '稀土ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '513630': '港股红利ETF',
}

HOLDINGS = ['510150', '510880', '512170', '512660', '513180', '515050', '515070', '515790', '588000', '159241', '159770']

results = {}

for ticker, name in ALL_TICKERS.items():
    try:
        print(f"Analyzing {ticker} ({name})...")
        data = fetch_stock_data(ticker, period='8mo')
        
        if data is None or data.empty:
            print(f"  WARNING: No data for {ticker}")
            continue
        
        # Calculate indicators
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        
        # Volume ratio (current / 20-day average)
        vol = data['Volume']
        vol_ma20 = vol.rolling(20).mean()
        vol_ratio = vol.iloc[-1] / vol_ma20.iloc[-1] if vol_ma20.iloc[-1] > 0 else 0
        
        # Bollinger %B
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        close = data['Close'].iloc[-1]
        pct_b = (close - lower) / (upper - lower) if (upper - lower) > 0 else 0.5
        
        # MACD status
        hist_current = macd_df['Histogram'].iloc[-1]
        hist_prev = macd_df['Histogram'].iloc[-2] if len(macd_df) > 1 else 0
        
        if hist_current > 0 and hist_prev > 0:
            macd_status = "金叉延续"
        elif hist_current > 0 and hist_prev <= 0:
            macd_status = "新金叉"
        elif hist_current <= 0 and hist_prev > 0:
            macd_status = "新死叉"
        else:
            macd_status = "死叉延续"
        
        # Price changes
        if len(data) >= 2:
            pct_1d = (data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100
        else:
            pct_1d = 0
            
        if len(data) >= 6:
            pct_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100
        else:
            pct_5d = 0

        # 10-day price change for extended trend view
        if len(data) >= 11:
            pct_10d = (data['Close'].iloc[-1] / data['Close'].iloc[-11] - 1) * 100
        else:
            pct_10d = 0
        
        results[ticker] = {
            'name': name,
            'close': float(data['Close'].iloc[-1]),
            'rsi': float(rsi_df['RSI'].iloc[-1]),
            'macd': float(macd_df['MACD'].iloc[-1]),
            'signal': float(macd_df['Signal'].iloc[-1]),
            'histogram': float(hist_current),
            'histogram_prev': float(hist_prev),
            'macd_status': macd_status,
            'bb_upper': float(upper),
            'bb_lower': float(lower),
            'bb_middle': float(bb_df['Middle'].iloc[-1]),
            'pct_b': float(pct_b),
            'volume_ratio': float(vol_ratio),
            'pct_1d': float(pct_1d),
            'pct_5d': float(pct_5d),
            'pct_10d': float(pct_10d),
            'is_holding': ticker in HOLDINGS,
            'date': str(data.index[-1].date()) if hasattr(data.index[-1], 'date') else str(data.index[-1]),
        }
        
        r = results[ticker]
        print(f"  Close={r['close']:.4f} RSI={r['rsi']:.1f} %B={r['pct_b']:.2f} MACD={r['macd_status']} Hist={r['histogram']:.4f} Vol={r['volume_ratio']:.2f} 1d={r['pct_1d']:.2f}% 5d={r['pct_5d']:.2f}%")
        
    except Exception as e:
        print(f"  ERROR analyzing {ticker}: {e}")
        import traceback
        traceback.print_exc()

# Save results
clean_results = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)

print(f"\n✅ Analysis complete! {len(results)} tickers analyzed.")
print(f"📁 Data saved to: {output_path}")

# Summary
print("\n=== SUMMARY ===")
print("\n--- Holdings ---")
for t in HOLDINGS:
    if t in results:
        r = results[t]
        print(f"  {t} {r['name']:10s} | RSI={r['rsi']:5.1f} | %B={r['pct_b']:5.2f} | {r['macd_status']:6s} | Hist={r['histogram']:+.4f} | Vol={r['volume_ratio']:.2f} | 1d={r['pct_1d']:+.2f}% | 5d={r['pct_5d']:+.2f}%")

print("\n--- Watchlist ---")
for t, name in ALL_TICKERS.items():
    if t not in HOLDINGS and t in results:
        r = results[t]
        print(f"  {t} {r['name']:10s} | RSI={r['rsi']:5.1f} | %B={r['pct_b']:5.2f} | {r['macd_status']:6s} | Hist={r['histogram']:+.4f} | Vol={r['volume_ratio']:.2f} | 1d={r['pct_1d']:+.2f}% | 5d={r['pct_5d']:+.2f}%")

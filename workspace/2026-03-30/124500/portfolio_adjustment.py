#!/usr/bin/env python3
"""
Portfolio Adjustment Technical Analysis - 2026-03-30
Analyzes all holdings + ETFs.csv watchlist with RSI, MACD, Bollinger Bands, Volume
"""
import sys, os, json
import pandas as pd
import numpy as np

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd,
    calculate_bollinger_bands, calculate_sma, calculate_atr,
    calculate_stochastic, fetch_realtime_quote
)
from scripts.utils import make_serializable

# ========== All tickers to analyze ==========
# Current holdings
HOLDINGS = {
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒指科技',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '561560': '电力ETF',
    '588000': '科创50',
    '603993': '洛阳钼业',
    '159770': '机器人AI',
}

# ETFs.csv watchlist (non-held)
WATCHLIST = {
    '159985': '豆粕ETF',
    '159689': '粮食ETF',
    '159870': '化工ETF',
    '561330': '矿业ETF',
    '159326': '电网设备ETF',
    '560280': '工程机械ETF',
    '159241': '航空航天ETF',
    '159830': '上海金ETF',
    '161226': '国投白银LOF',
    '159516': '半导体设备ETF',
    '513630': '港股红利ETF',
}

ALL_TICKERS = {**HOLDINGS, **WATCHLIST}

def analyze_ticker(ticker, name):
    """Full technical analysis for one ticker"""
    result = {'ticker': ticker, 'name': name, 'is_holding': ticker in HOLDINGS}
    
    try:
        # Fetch 8 months of daily data
        data = fetch_stock_data(ticker, period='8mo')
        if data is None or len(data) < 30:
            result['error'] = f'Insufficient data: {len(data) if data is not None else 0} rows'
            return result
        
        # Current price info
        result['latest_close'] = float(data['Close'].iloc[-1])
        result['prev_close'] = float(data['Close'].iloc[-2]) if len(data) > 1 else None
        
        # RSI
        rsi_df = calculate_rsi(data, window=14)
        result['rsi'] = float(rsi_df['RSI'].iloc[-1])
        result['rsi_prev'] = float(rsi_df['RSI'].iloc[-2]) if len(rsi_df) > 1 else None
        # RSI 5-day trend
        if len(rsi_df) >= 5:
            result['rsi_5d_ago'] = float(rsi_df['RSI'].iloc[-5])
        
        # MACD
        macd_df = calculate_macd(data)
        result['macd'] = float(macd_df['MACD'].iloc[-1])
        result['macd_signal'] = float(macd_df['Signal'].iloc[-1])
        result['macd_hist'] = float(macd_df['Histogram'].iloc[-1])
        result['macd_hist_prev'] = float(macd_df['Histogram'].iloc[-2]) if len(macd_df) > 1 else None
        # MACD cross detection
        if len(macd_df) >= 2:
            prev_hist = macd_df['Histogram'].iloc[-2]
            curr_hist = macd_df['Histogram'].iloc[-1]
            if prev_hist < 0 and curr_hist >= 0:
                result['macd_cross'] = 'golden_cross'
            elif prev_hist > 0 and curr_hist < 0:
                result['macd_cross'] = 'death_cross'
            elif curr_hist > 0:
                result['macd_cross'] = 'above_zero'
            else:
                result['macd_cross'] = 'below_zero'
            # Trend: converging or diverging
            if curr_hist < 0 and abs(curr_hist) < abs(prev_hist):
                result['macd_trend'] = 'converging'  # 死叉收窄
            elif curr_hist < 0 and abs(curr_hist) > abs(prev_hist):
                result['macd_trend'] = 'diverging'  # 死叉加深
            elif curr_hist > 0 and curr_hist > prev_hist:
                result['macd_trend'] = 'strengthening'  # 金叉走强
            elif curr_hist > 0 and curr_hist < prev_hist:
                result['macd_trend'] = 'weakening'  # 金叉走弱
            else:
                result['macd_trend'] = 'flat'
        
        # Bollinger Bands
        bb_df = calculate_bollinger_bands(data)
        upper = float(bb_df['Upper'].iloc[-1])
        lower = float(bb_df['Lower'].iloc[-1])
        middle = float(bb_df['Middle'].iloc[-1])
        close_price = float(data['Close'].iloc[-1])
        if upper != lower:
            result['bb_pct_b'] = (close_price - lower) / (upper - lower)
        else:
            result['bb_pct_b'] = 0.5
        result['bb_upper'] = upper
        result['bb_middle'] = middle
        result['bb_lower'] = lower
        result['bb_width'] = (upper - lower) / middle if middle != 0 else 0
        
        # SMA
        sma20_df = calculate_sma(data, window=20)
        sma60_df = calculate_sma(data, window=60)
        result['sma20'] = float(sma20_df['SMA'].iloc[-1])
        result['sma60'] = float(sma60_df['SMA'].iloc[-1]) if len(sma60_df) > 0 and not pd.isna(sma60_df['SMA'].iloc[-1]) else None
        result['above_sma20'] = close_price > result['sma20']
        if result['sma60'] is not None:
            result['above_sma60'] = close_price > result['sma60']
        
        # ATR (volatility)
        atr_df = calculate_atr(data, window=14)
        result['atr'] = float(atr_df['ATR'].iloc[-1])
        result['atr_pct'] = result['atr'] / close_price * 100  # ATR as % of price
        
        # Stochastic
        stoch_df = calculate_stochastic(data)
        result['stoch_k'] = float(stoch_df['K'].iloc[-1])
        result['stoch_d'] = float(stoch_df['D'].iloc[-1])
        
        # Volume analysis
        if 'Volume' in data.columns:
            vol = data['Volume']
            result['volume_latest'] = float(vol.iloc[-1])
            vol_ma20 = vol.rolling(20).mean()
            if not pd.isna(vol_ma20.iloc[-1]) and vol_ma20.iloc[-1] > 0:
                result['vol_ratio'] = float(vol.iloc[-1] / vol_ma20.iloc[-1])
            else:
                result['vol_ratio'] = None
        
        # Price changes
        closes = data['Close']
        if len(closes) >= 2:
            result['change_1d'] = float((closes.iloc[-1] / closes.iloc[-2] - 1) * 100)
        if len(closes) >= 6:
            result['change_5d'] = float((closes.iloc[-1] / closes.iloc[-6] - 1) * 100)
        if len(closes) >= 11:
            result['change_10d'] = float((closes.iloc[-1] / closes.iloc[-11] - 1) * 100)
        if len(closes) >= 21:
            result['change_20d'] = float((closes.iloc[-1] / closes.iloc[-21] - 1) * 100)
        
        result['status'] = 'ok'
        
    except Exception as e:
        result['error'] = str(e)
        result['status'] = 'error'
    
    return result

def main():
    print("=" * 60)
    print("Portfolio Technical Analysis - 2026-03-30")
    print("=" * 60)
    
    all_results = {}
    
    for ticker, name in ALL_TICKERS.items():
        print(f"\nAnalyzing {name} ({ticker})...")
        result = analyze_ticker(ticker, name)
        all_results[ticker] = result
        
        if result.get('status') == 'ok':
            print(f"  RSI={result['rsi']:.1f} | %B={result['bb_pct_b']:.2f} | "
                  f"MACD_Hist={result['macd_hist']:.4f} | "
                  f"VolRatio={result.get('vol_ratio', 'N/A')}")
        else:
            print(f"  ERROR: {result.get('error', 'unknown')}")
    
    # Fetch realtime quotes
    print("\n\nFetching realtime quotes...")
    try:
        all_ticker_list = list(ALL_TICKERS.keys())
        rt_quotes = fetch_realtime_quote(all_ticker_list)
        if rt_quotes is not None:
            rt_data = rt_quotes.to_dict('records') if hasattr(rt_quotes, 'to_dict') else []
            all_results['_realtime_quotes'] = rt_data
            print(f"  Got {len(rt_data)} realtime quotes")
    except Exception as e:
        print(f"  Realtime quotes error: {e}")
        all_results['_realtime_quotes'] = []
    
    # Save results
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    clean = make_serializable(all_results)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nResults saved to {output_path}")
    print(f"Total tickers analyzed: {len(ALL_TICKERS)}")
    
    # Print summary table
    print("\n" + "=" * 120)
    print(f"{'Name':<14} {'RSI':>6} {'%B':>6} {'MACD_H':>10} {'Cross':>12} {'Trend':>14} {'StochK':>7} {'VolR':>6} {'1D%':>7} {'5D%':>7} {'10D%':>7}")
    print("-" * 120)
    
    for ticker, name in ALL_TICKERS.items():
        r = all_results[ticker]
        if r.get('status') != 'ok':
            print(f"{name:<14} ERROR: {r.get('error','?')}")
            continue
        print(f"{name:<14} {r['rsi']:>6.1f} {r['bb_pct_b']:>6.2f} {r['macd_hist']:>10.4f} "
              f"{r.get('macd_cross','?'):>12} {r.get('macd_trend','?'):>14} "
              f"{r.get('stoch_k',0):>7.1f} {r.get('vol_ratio','?'):>6} "
              f"{r.get('change_1d',0):>7.2f} {r.get('change_5d',0):>7.2f} {r.get('change_10d',0):>7.2f}")

if __name__ == '__main__':
    main()

import os
import sys
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.claude/skills/quantitative-trading'))
sys.path.insert(0, SKILL_DIR)

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scripts.utils import make_serializable
from scripts import (
    fetch_stock_data,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_ema, calculate_atr
)
from scripts import RiskManager

TICKERS = ['AMD', 'NVDA', 'GOOG']
TOTAL_CAPITAL = 8454.0
TODAY = datetime.today().strftime('%Y-%m-%d')

def analyze_ticker(ticker):
    print(f"\n{'='*50}")
    print(f"Analyzing {ticker}...")

    data = fetch_stock_data(ticker, period='6mo')
    if data is None or data.empty:
        print(f"  ERROR: No data for {ticker}")
        return None

    close = data['Close']
    volume = data['Volume']

    # ---- Indicators ----
    rsi_df    = calculate_rsi(data, window=14)
    macd_df   = calculate_macd(data)
    bb_df     = calculate_bollinger_bands(data)
    sma20_df  = calculate_sma(data, window=20)
    sma50_df  = calculate_sma(data, window=50)
    ema12_df  = calculate_ema(data, window=12)
    atr_df    = calculate_atr(data, window=14)

    price       = float(close.iloc[-1])
    rsi         = float(rsi_df['RSI'].iloc[-1])
    macd_val    = float(macd_df['MACD'].iloc[-1])
    macd_sig    = float(macd_df['Signal'].iloc[-1])
    macd_hist   = float(macd_df['Histogram'].iloc[-1])
    bb_upper    = float(bb_df['Upper'].iloc[-1])
    bb_middle   = float(bb_df['Middle'].iloc[-1])
    bb_lower    = float(bb_df['Lower'].iloc[-1])
    bb_pct_b    = (price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
    sma20       = float(sma20_df['SMA'].iloc[-1])
    sma50       = float(sma50_df['SMA'].iloc[-1])
    atr         = float(atr_df['ATR'].iloc[-1])

    vol_recent   = float(volume.iloc[-1])
    vol_avg20    = float(volume.iloc[-20:].mean())
    vol_ratio    = vol_recent / vol_avg20 if vol_avg20 > 0 else 1.0

    # ---- 52-week high/low ----
    data_1y = fetch_stock_data(ticker, period='1y')
    high_52w = float(data_1y['High'].max()) if data_1y is not None else price
    low_52w  = float(data_1y['Low'].min())  if data_1y is not None else price
    pct_from_high = (price - high_52w) / high_52w * 100
    pct_from_low  = (price - low_52w)  / low_52w  * 100

    # ---- Recent returns ----
    ret_5d  = float((close.iloc[-1] / close.iloc[-6]  - 1) * 100) if len(close) >= 6  else 0
    ret_20d = float((close.iloc[-1] / close.iloc[-21] - 1) * 100) if len(close) >= 21 else 0

    # ---- Risk metrics ----
    rm = RiskManager()
    returns = close.pct_change().dropna()
    var_95 = rm.calculate_var(returns, confidence_level=0.95)
    drawdown = rm.calculate_drawdown_metrics(returns, is_returns=True)

    print(f"  Price: ${price:.2f} | RSI: {rsi:.1f} | MACD hist: {macd_hist:.3f}")
    print(f"  BB %B: {bb_pct_b:.2f} | SMA20: {sma20:.2f} | SMA50: {sma50:.2f}")
    print(f"  ATR: {atr:.2f} ({atr/price*100:.1f}%) | Vol ratio: {vol_ratio:.2f}x")
    print(f"  52w high: ${high_52w:.2f} ({pct_from_high:.1f}%) | 52w low: ${low_52w:.2f} ({pct_from_low:.1f}%)")

    return {
        'ticker': ticker,
        'price': price,
        'rsi': rsi,
        'macd': macd_val,
        'macd_signal': macd_sig,
        'macd_hist': macd_hist,
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'bb_pct_b': bb_pct_b,
        'sma20': sma20,
        'sma50': sma50,
        'atr': atr,
        'atr_pct': atr / price * 100,
        'vol_ratio': vol_ratio,
        'high_52w': high_52w,
        'low_52w': low_52w,
        'pct_from_high': pct_from_high,
        'pct_from_low': pct_from_low,
        'ret_5d': ret_5d,
        'ret_20d': ret_20d,
        'var_95': float(var_95),
        'max_drawdown': float(drawdown.get('max_drawdown', 0)),
        'data_len': len(close),
    }


def fetch_sentiment():
    """Fetch US market news via web search keywords."""
    keywords = {
        'AMD':  'AMD Advanced Micro Devices stock news 2026',
        'NVDA': 'NVIDIA NVDA stock news earnings 2026',
        'GOOG': 'Google Alphabet GOOG stock news 2026',
        'macro': 'US stock market outlook May 2026 Fed rate',
        'semiconductors': 'semiconductor chip sector outlook 2026',
    }
    print("\n[Sentiment] Using web search for US market context...")
    return keywords  # web search to be done by agent inline


def score_entry(info):
    """Score entry attractiveness (0-100) based on technical signals."""
    score = 50
    reasons = []

    rsi = info['rsi']
    bb_b = info['bb_pct_b']
    macd_h = info['macd_hist']
    vol_r = info['vol_ratio']
    p_from_high = info['pct_from_high']

    # RSI
    if rsi < 35:
        score += 20; reasons.append(f"RSI超卖({rsi:.0f}，偏多)")
    elif rsi < 50:
        score += 10; reasons.append(f"RSI健康区({rsi:.0f}，中性偏多)")
    elif rsi > 70:
        score -= 20; reasons.append(f"RSI超买({rsi:.0f}，偏空)")
    elif rsi > 60:
        score -= 8;  reasons.append(f"RSI偏高({rsi:.0f}，需谨慎)")
    else:
        reasons.append(f"RSI中性({rsi:.0f})")

    # Bollinger %B
    if bb_b < 0.2:
        score += 15; reasons.append(f"布林下轨附近(%B={bb_b:.2f}，超卖支撑)")
    elif bb_b < 0.4:
        score += 8;  reasons.append(f"布林中下位(%B={bb_b:.2f}，有支撑)")
    elif bb_b > 0.85:
        score -= 15; reasons.append(f"布林上轨附近(%B={bb_b:.2f}，压力大)")
    elif bb_b > 0.65:
        score -= 5;  reasons.append(f"布林中上位(%B={bb_b:.2f}，偏强但需注意)")
    else:
        reasons.append(f"布林中位区(%B={bb_b:.2f}，中性)")

    # MACD
    if macd_h > 0:
        score += 10; reasons.append("MACD柱正值(多头)")
    else:
        score -= 10; reasons.append("MACD柱负值(空头)")

    # Price vs SMA
    price = info['price']
    if price > info['sma20'] > info['sma50']:
        score += 10; reasons.append("价格在SMA20/50上方(多头排列)")
    elif price < info['sma20'] and price < info['sma50']:
        score -= 10; reasons.append("价格在SMA20/50下方(空头排列)")
    else:
        reasons.append("价格在均线间(整理)")

    # Volume
    if vol_r > 1.5:
        score += 5;  reasons.append(f"成交量放大({vol_r:.1f}x均量，有资金关注)")
    elif vol_r < 0.5:
        score -= 5;  reasons.append(f"成交量萎缩({vol_r:.1f}x均量，参与度低)")

    # Distance from 52w high (not chasing tops)
    if p_from_high < -30:
        score += 10; reasons.append(f"距52周高点-{abs(p_from_high):.0f}%，有修复空间")
    elif p_from_high < -15:
        score += 5;  reasons.append(f"距52周高点-{abs(p_from_high):.0f}%，合理回调")
    elif p_from_high > -5:
        score -= 10; reasons.append(f"接近52周高点，追高风险")

    score = max(0, min(100, score))
    return score, reasons


def suggest_allocation(results, total_capital):
    """Suggest position sizing based on entry scores and ATR-based risk."""
    scored = [(r, *score_entry(r)) for r in results if r]
    scored.sort(key=lambda x: x[1], reverse=True)

    suggestions = []
    for info, score, reasons in scored:
        ticker = info['ticker']
        price  = info['price']
        atr    = info['atr']

        # Risk: 1.5% of capital per trade (stop = 2x ATR)
        risk_per_trade = total_capital * 0.015
        stop_distance  = atr * 2
        shares_by_risk = int(risk_per_trade / stop_distance) if stop_distance > 0 else 0

        # Cap at 35% of capital per position
        max_shares_by_cap = int(total_capital * 0.35 / price)
        shares = min(shares_by_risk, max_shares_by_cap)

        position_value = shares * price
        pct_of_capital = position_value / total_capital * 100

        verdict = "建议建仓" if score >= 58 else ("可小仓位试探" if score >= 45 else "暂不建仓")

        suggestions.append({
            'ticker': ticker,
            'score': score,
            'price': price,
            'shares': shares,
            'position_value': round(position_value, 2),
            'pct_of_capital': round(pct_of_capital, 1),
            'stop_loss': round(price - stop_distance, 2),
            'atr': round(atr, 2),
            'verdict': verdict,
            'reasons': reasons,
        })

    return suggestions


# ---- Main ----
results = []
for ticker in TICKERS:
    r = analyze_ticker(ticker)
    if r:
        results.append(r)

suggestions = suggest_allocation(results, TOTAL_CAPITAL)

# Save data
output_data = {
    'analysis_date': TODAY,
    'total_capital': TOTAL_CAPITAL,
    'tickers': results,
    'suggestions': suggestions,
}
clean = make_serializable(output_data)
with open(os.path.join(SCRIPT_DIR, 'us_stock_analysis_data.json'), 'w', encoding='utf-8') as f:
    json.dump(clean, f, indent=2, ensure_ascii=False)

print("\n\n" + "="*60)
print("SUMMARY — ENTRY ANALYSIS")
print("="*60)
total_invest = 0
for s in suggestions:
    print(f"\n{s['ticker']}  得分:{s['score']}/100  → {s['verdict']}")
    print(f"  价格: ${s['price']:.2f}  建议股数: {s['shares']}股  仓位: ${s['position_value']:.0f} ({s['pct_of_capital']:.1f}%)")
    print(f"  止损位: ${s['stop_loss']:.2f}  ATR: ${s['atr']:.2f}")
    for r in s['reasons']:
        print(f"    · {r}")
    total_invest += s['position_value']

print(f"\n合计建议投入: ${total_invest:.0f} / ${TOTAL_CAPITAL:.0f}  剩余现金: ${TOTAL_CAPITAL - total_invest:.0f}")
print(f"\nData saved to: {SCRIPT_DIR}/us_stock_analysis_data.json")

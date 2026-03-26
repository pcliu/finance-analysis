#!/usr/bin/env python3
"""
Gold & Silver Technical Analysis - Bottom Fishing Assessment
Date: 2026-03-25
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd, 
    calculate_bollinger_bands, calculate_sma, calculate_atr,
    calculate_stochastic
)
from scripts.utils import make_serializable

def analyze_asset(ticker, name, period='6mo'):
    """Comprehensive technical analysis for a single asset"""
    print(f"\n{'='*60}")
    print(f"Analyzing: {name} ({ticker})")
    print(f"{'='*60}")
    
    try:
        data = fetch_stock_data(ticker, period=period)
        if data is None or data.empty:
            print(f"  ❌ No data for {ticker}")
            return None
    except Exception as e:
        print(f"  ❌ Error fetching {ticker}: {e}")
        return None
    
    # Current price info
    current_price = float(data['Close'].iloc[-1])
    prev_close = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
    daily_change = ((current_price - prev_close) / prev_close) * 100
    
    # Price range analysis (recent high/low)
    high_52w = float(data['High'].max())
    low_52w = float(data['Low'].min())
    high_1m = float(data['High'].tail(22).max())
    low_1m = float(data['Low'].tail(22).min())
    
    # Drawdown from recent high
    drawdown_from_high = ((current_price - high_52w) / high_52w) * 100
    drawdown_from_1m_high = ((current_price - high_1m) / high_1m) * 100
    
    # Technical Indicators
    rsi = calculate_rsi(data, window=14)
    macd = calculate_macd(data)
    bb = calculate_bollinger_bands(data)
    sma_20 = calculate_sma(data, window=20)
    sma_50 = calculate_sma(data, window=50)
    sma_200 = calculate_sma(data, window=200)
    atr = calculate_atr(data, window=14)
    stoch = calculate_stochastic(data)
    
    # Get latest values
    current_rsi = float(rsi['RSI'].iloc[-1])
    rsi_prev = float(rsi['RSI'].iloc[-2]) if len(rsi) > 1 else current_rsi
    
    macd_line = float(macd['MACD'].iloc[-1])
    signal_line = float(macd['Signal'].iloc[-1])
    histogram = float(macd['Histogram'].iloc[-1])
    prev_histogram = float(macd['Histogram'].iloc[-2]) if len(macd) > 1 else histogram
    
    bb_upper = float(bb['Upper'].iloc[-1])
    bb_middle = float(bb['Middle'].iloc[-1])
    bb_lower = float(bb['Lower'].iloc[-1])
    bb_width = (bb_upper - bb_lower) / bb_middle * 100
    
    sma20_val = float(sma_20['SMA'].iloc[-1])
    sma50_val = float(sma_50['SMA'].iloc[-1])
    sma200_val = float(sma_200['SMA'].iloc[-1]) if not sma_200['SMA'].isna().iloc[-1] else None
    
    atr_val = float(atr['ATR'].iloc[-1])
    atr_pct = (atr_val / current_price) * 100
    
    stoch_k = float(stoch['K'].iloc[-1])
    stoch_d = float(stoch['D'].iloc[-1])
    
    # Volume analysis
    avg_vol_20 = float(data['Volume'].tail(20).mean())
    latest_vol = float(data['Volume'].iloc[-1])
    vol_ratio = latest_vol / avg_vol_20 if avg_vol_20 > 0 else 1.0
    
    # RSI divergence check (simplified)
    # Check if price is making new lows but RSI is not
    price_5d_ago = float(data['Close'].iloc[-5]) if len(data) >= 5 else current_price
    rsi_5d_ago = float(rsi['RSI'].iloc[-5]) if len(rsi) >= 5 else current_rsi
    bullish_divergence = (current_price < price_5d_ago) and (current_rsi > rsi_5d_ago)
    
    # MACD histogram divergence
    macd_converging = abs(histogram) < abs(prev_histogram) and histogram < 0
    
    # Bollinger position
    bb_position = (current_price - bb_lower) / (bb_upper - bb_lower) * 100 if (bb_upper - bb_lower) > 0 else 50
    
    # Determine signals
    signals = []
    score = 0  # -10 to +10 scale, positive = buy signal
    
    # RSI signals
    if current_rsi < 30:
        signals.append(f"🟢 RSI 超卖 ({current_rsi:.1f})")
        score += 3
    elif current_rsi < 40:
        signals.append(f"🟡 RSI 偏低 ({current_rsi:.1f})")
        score += 1
    elif current_rsi > 70:
        signals.append(f"🔴 RSI 超买 ({current_rsi:.1f})")
        score -= 2
    else:
        signals.append(f"⚪ RSI 中性 ({current_rsi:.1f})")
    
    # MACD signals
    if macd_line > signal_line and macd_converging:
        signals.append("🟢 MACD 金叉形成中")
        score += 2
    elif histogram > prev_histogram and histogram < 0:
        signals.append("🟡 MACD 柱状图收窄（空头力量减弱）")
        score += 1
    elif macd_line < signal_line:
        signals.append("🔴 MACD 死叉")
        score -= 1
    
    # Bollinger Bands
    if current_price <= bb_lower:
        signals.append(f"🟢 触及布林带下轨（超卖区域）")
        score += 2
    elif bb_position < 20:
        signals.append(f"🟡 接近布林带下轨 (位置={bb_position:.0f}%)")
        score += 1
    elif current_price >= bb_upper:
        signals.append(f"🔴 触及布林带上轨（超买区域）")
        score -= 1
    
    # SMA signals
    if current_price > sma20_val:
        signals.append("🟢 价格在20日均线上方")
        score += 1
    else:
        signals.append("🔴 价格在20日均线下方")
        score -= 1
    
    if current_price > sma50_val:
        signals.append("🟢 价格在50日均线上方")
        score += 1
    else:
        signals.append("🟡 价格在50日均线下方")
    
    if sma200_val and current_price > sma200_val:
        signals.append("🟢 价格在200日均线上方（长期趋势向上）")
        score += 1
    elif sma200_val:
        signals.append("🔴 价格在200日均线下方")
        score -= 1
    
    # Stochastic
    if stoch_k < 20:
        signals.append(f"🟢 随机指标超卖 (K={stoch_k:.1f})")
        score += 2
    elif stoch_k < 30:
        signals.append(f"🟡 随机指标偏低 (K={stoch_k:.1f})")
        score += 1
    elif stoch_k > 80:
        signals.append(f"🔴 随机指标超买 (K={stoch_k:.1f})")
        score -= 1
    
    # Volume confirmation
    if vol_ratio > 1.5:
        signals.append(f"📊 放量 (成交量比={vol_ratio:.1f}x)")
    elif vol_ratio < 0.7:
        signals.append(f"📊 缩量 (成交量比={vol_ratio:.1f}x)")
    
    # RSI divergence
    if bullish_divergence:
        signals.append("🟢 RSI 底部背离（看涨信号）")
        score += 2
    
    # ATR / Volatility
    if atr_pct > 3:
        signals.append(f"⚠️ 波动率较高 (ATR%={atr_pct:.1f}%)")
    
    # Overall assessment
    if score >= 5:
        overall = "🟢 强烈买入信号"
    elif score >= 3:
        overall = "🟢 可考虑分批建仓"
    elif score >= 1:
        overall = "🟡 观望，等待更多确认信号"
    elif score >= -1:
        overall = "⚪ 中性，不急于操作"
    else:
        overall = "🔴 暂不建议抄底"
    
    result = {
        'ticker': ticker,
        'name': name,
        'current_price': current_price,
        'daily_change_pct': daily_change,
        'high_period': high_52w,
        'low_period': low_52w,
        'high_1m': high_1m,
        'low_1m': low_1m,
        'drawdown_from_high': drawdown_from_high,
        'drawdown_from_1m_high': drawdown_from_1m_high,
        'rsi': current_rsi,
        'rsi_prev': rsi_prev,
        'macd': macd_line,
        'signal': signal_line,
        'histogram': histogram,
        'prev_histogram': prev_histogram,
        'bb_upper': bb_upper,
        'bb_middle': bb_middle,
        'bb_lower': bb_lower,
        'bb_width': bb_width,
        'bb_position': bb_position,
        'sma_20': sma20_val,
        'sma_50': sma50_val,
        'sma_200': sma200_val,
        'atr': atr_val,
        'atr_pct': atr_pct,
        'stoch_k': stoch_k,
        'stoch_d': stoch_d,
        'avg_volume_20d': avg_vol_20,
        'latest_volume': latest_vol,
        'volume_ratio': vol_ratio,
        'bullish_divergence': bullish_divergence,
        'macd_converging': macd_converging,
        'signals': signals,
        'score': score,
        'overall': overall
    }
    
    # Print summary
    print(f"  价格: ${current_price:.2f} ({daily_change:+.2f}%)")
    print(f"  从高点回撤: {drawdown_from_high:.1f}%")
    print(f"  近1月回撤: {drawdown_from_1m_high:.1f}%")
    print(f"  RSI(14): {current_rsi:.1f}")
    print(f"  MACD: {macd_line:.4f} / Signal: {signal_line:.4f}")
    print(f"  布林带位置: {bb_position:.0f}%")
    print(f"  Stochastic K/D: {stoch_k:.1f}/{stoch_d:.1f}")
    print(f"  成交量比: {vol_ratio:.2f}x")
    print(f"  ATR%: {atr_pct:.1f}%")
    print(f"  综合评分: {score}/10")
    print(f"  ⇒ {overall}")
    print(f"  信号:")
    for s in signals:
        print(f"    {s}")
    
    return result


def main():
    # Assets to analyze
    assets = [
        ('GC=F', '黄金期货 (COMEX Gold)', '1y'),
        ('SI=F', '白银期货 (COMEX Silver)', '1y'),
        ('GLD', '黄金 ETF (SPDR Gold Trust)', '1y'),
        ('SLV', '白银 ETF (iShares Silver Trust)', '1y'),
        ('IAU', '黄金 ETF (iShares Gold)', '1y'),
    ]
    
    results = {}
    for ticker, name, period in assets:
        result = analyze_asset(ticker, name, period)
        if result:
            results[ticker] = result
    
    # Save results
    clean_results = make_serializable(results)
    output_path = os.path.join(SCRIPT_DIR, 'gold_silver_analysis_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n\n{'='*60}")
    print("分析结果已保存到:", output_path)
    print(f"{'='*60}")
    
    # Summary
    print("\n📊 综合评估摘要:")
    for ticker, r in results.items():
        print(f"  {r['name']}: 评分 {r['score']}/10 → {r['overall']}")

if __name__ == '__main__':
    main()

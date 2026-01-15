#!/usr/bin/env python3
"""Portfolio analysis script for current holdings and potential new positions."""

import sys
import os
import json
from datetime import datetime

# Setup path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading')

from scripts import (
    fetch_stock_data, 
    calculate_rsi, 
    calculate_sma, 
    calculate_macd,
    calculate_bollinger_bands,
    calculate_ema
)

# Current holdings from user screenshot
current_holdings = [
    {"code": "510880", "name": "红利ETF", "shares": 1000, "market_value": 3233.00, "pnl": 27.00, "pnl_pct": 0.86},
    {"code": "512400", "name": "有色ETF", "shares": 700, "market_value": 1504.30, "pnl": 93.40, "pnl_pct": 6.66},
    {"code": "513180", "name": "恒指科技", "shares": 800, "market_value": 606.40, "pnl": -9.00, "pnl_pct": -1.38},
    {"code": "513630", "name": "香港红利", "shares": 1000, "market_value": 1614.00, "pnl": -1.00, "pnl_pct": -0.03},
    {"code": "515050", "name": "5GETF", "shares": 500, "market_value": 1165.50, "pnl": 1.50, "pnl_pct": 0.17},
    {"code": "515070", "name": "AI智能", "shares": 500, "market_value": 1044.50, "pnl": 48.50, "pnl_pct": 4.92},
    {"code": "588000", "name": "科创50", "shares": 6000, "market_value": 9396.60, "pnl": 1184.10, "pnl_pct": 14.42},
    {"code": "159770", "name": "机器人AI", "shares": 1000, "market_value": 1106.00, "pnl": 37.00, "pnl_pct": 3.51},
    {"code": "159830", "name": "上海金", "shares": 400, "market_value": 4063.60, "pnl": 174.30, "pnl_pct": 4.49},
    {"code": "161226", "name": "白银基金", "shares": 300, "market_value": 834.00, "pnl": 187.60, "pnl_pct": 29.12},
]

# Potential new positions
candidates = [
    {"code": "159241", "name": "航空航天ETF天弘"},
    {"code": "510150", "name": "消费ETF"},
    {"code": "512660", "name": "军工ETF"},
    {"code": "159516", "name": "半导体设备ETF"},
]

def convert_to_tushare_code(code):
    """Convert short code to tushare format."""
    if code.startswith("6"):
        return f"{code}.SH"
    elif code.startswith("5"):
        if code.startswith("51") or code.startswith("58"):
            return f"{code}.SH"
    elif code.startswith("1"):
        return f"{code}.SZ"
    return f"{code}.SZ"

def analyze_stock(ticker, name, period='3mo'):
    """Analyze a single stock and return technical indicators."""
    try:
        data = fetch_stock_data(ticker, period=period, market='cn')
        
        if data is None or len(data) < 20:
            return {"error": f"Insufficient data for {ticker}"}
        
        # Calculate indicators
        rsi = calculate_rsi(data, period=14)
        sma_5 = calculate_sma(data, window=5)
        sma_10 = calculate_sma(data, window=10)
        sma_20 = calculate_sma(data, window=20)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data, window=20)
        ema_12 = calculate_ema(data, window=12)
        
        current_price = float(data['Close'].iloc[-1])
        
        # Get last valid values
        rsi_val = float(rsi.dropna().iloc[-1]) if len(rsi.dropna()) > 0 else None
        sma_5_val = float(sma_5.dropna().iloc[-1]) if len(sma_5.dropna()) > 0 else None
        sma_10_val = float(sma_10.dropna().iloc[-1]) if len(sma_10.dropna()) > 0 else None
        sma_20_val = float(sma_20.dropna().iloc[-1]) if len(sma_20.dropna()) > 0 else None
        ema_12_val = float(ema_12.dropna().iloc[-1]) if len(ema_12.dropna()) > 0 else None
        
        macd_val = float(macd['MACD'].dropna().iloc[-1]) if len(macd['MACD'].dropna()) > 0 else None
        signal_val = float(macd['Signal'].dropna().iloc[-1]) if len(macd['Signal'].dropna()) > 0 else None
        histogram_val = float(macd['Histogram'].dropna().iloc[-1]) if len(macd['Histogram'].dropna()) > 0 else None
        
        bb_upper = float(bb['Upper'].dropna().iloc[-1]) if len(bb['Upper'].dropna()) > 0 else None
        bb_middle = float(bb['Middle'].dropna().iloc[-1]) if len(bb['Middle'].dropna()) > 0 else None
        bb_lower = float(bb['Lower'].dropna().iloc[-1]) if len(bb['Lower'].dropna()) > 0 else None
        
        # Recent price changes
        price_5d_ago = float(data['Close'].iloc[-5]) if len(data) >= 5 else current_price
        price_20d_ago = float(data['Close'].iloc[-20]) if len(data) >= 20 else current_price
        change_5d = (current_price - price_5d_ago) / price_5d_ago * 100
        change_20d = (current_price - price_20d_ago) / price_20d_ago * 100
        
        # Volume analysis
        vol_avg = float(data['Volume'].tail(20).mean()) if 'Volume' in data.columns else 0
        vol_recent = float(data['Volume'].tail(5).mean()) if 'Volume' in data.columns else 0
        vol_ratio = vol_recent / vol_avg if vol_avg > 0 else 1
        
        # Trend determination
        trend = "横盘"
        if sma_5_val and sma_10_val and sma_20_val:
            if sma_5_val > sma_10_val > sma_20_val and current_price > sma_5_val:
                trend = "强势上涨"
            elif sma_5_val > sma_10_val and current_price > sma_20_val:
                trend = "上涨"
            elif sma_5_val < sma_10_val < sma_20_val and current_price < sma_5_val:
                trend = "强势下跌"
            elif sma_5_val < sma_10_val and current_price < sma_20_val:
                trend = "下跌"
        
        # RSI interpretation
        rsi_status = "中性"
        if rsi_val:
            if rsi_val < 30:
                rsi_status = "超卖"
            elif rsi_val < 40:
                rsi_status = "偏弱"
            elif rsi_val > 70:
                rsi_status = "超买"
            elif rsi_val > 60:
                rsi_status = "偏强"
        
        # MACD signal
        macd_signal = "中性"
        if macd_val and signal_val:
            if macd_val > signal_val and histogram_val > 0:
                macd_signal = "看多"
            elif macd_val < signal_val and histogram_val < 0:
                macd_signal = "看空"
        
        # Support and resistance based on Bollinger Bands
        support = bb_lower
        resistance = bb_upper
        
        return {
            "ticker": ticker,
            "name": name,
            "current_price": round(current_price, 3),
            "rsi": round(rsi_val, 2) if rsi_val else None,
            "rsi_status": rsi_status,
            "sma_5": round(sma_5_val, 3) if sma_5_val else None,
            "sma_10": round(sma_10_val, 3) if sma_10_val else None,
            "sma_20": round(sma_20_val, 3) if sma_20_val else None,
            "ema_12": round(ema_12_val, 3) if ema_12_val else None,
            "macd": round(macd_val, 4) if macd_val else None,
            "macd_signal": round(signal_val, 4) if signal_val else None,
            "macd_histogram": round(histogram_val, 4) if histogram_val else None,
            "macd_interpretation": macd_signal,
            "bb_upper": round(bb_upper, 3) if bb_upper else None,
            "bb_middle": round(bb_middle, 3) if bb_middle else None,
            "bb_lower": round(bb_lower, 3) if bb_lower else None,
            "trend": trend,
            "change_5d_pct": round(change_5d, 2),
            "change_20d_pct": round(change_20d, 2),
            "vol_ratio": round(vol_ratio, 2),
            "support": round(support, 3) if support else None,
            "resistance": round(resistance, 3) if resistance else None,
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker, "name": name}

def main():
    output_dir = "/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading/workspace/2026-01-12/092826"
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("开始分析当前持仓...")
    print("=" * 60)
    
    holdings_analysis = []
    for h in current_holdings:
        ticker = convert_to_tushare_code(h["code"])
        print(f"分析 {h['name']} ({ticker})...")
        result = analyze_stock(ticker, h["name"])
        result["shares"] = h["shares"]
        result["market_value"] = h["market_value"]
        result["pnl"] = h["pnl"]
        result["pnl_pct"] = h["pnl_pct"]
        result["original_code"] = h["code"]
        holdings_analysis.append(result)
    
    print("\n" + "=" * 60)
    print("分析候选标的...")
    print("=" * 60)
    
    candidates_analysis = []
    for c in candidates:
        ticker = convert_to_tushare_code(c["code"])
        print(f"分析 {c['name']} ({ticker})...")
        result = analyze_stock(ticker, c["name"])
        result["original_code"] = c["code"]
        candidates_analysis.append(result)
    
    # Save results
    results = {
        "analysis_time": datetime.now().isoformat(),
        "total_holdings_value": sum(h["market_value"] for h in current_holdings),
        "total_pnl": sum(h["pnl"] for h in current_holdings),
        "available_cash": 69785.86,
        "max_increase_limit": 10000,
        "holdings_analysis": holdings_analysis,
        "candidates_analysis": candidates_analysis
    }
    
    with open(f"{output_dir}/analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析结果已保存至: {output_dir}/analysis_results.json")
    
    # Print summary
    print("\n" + "=" * 60)
    print("持仓分析摘要")
    print("=" * 60)
    for h in holdings_analysis:
        if "error" not in h:
            print(f"\n{h['name']} ({h.get('original_code', 'N/A')})")
            print(f"  当前价: {h['current_price']} | RSI: {h['rsi']} ({h['rsi_status']})")
            print(f"  趋势: {h['trend']} | MACD: {h['macd_interpretation']}")
            print(f"  5日涨跌: {h['change_5d_pct']}% | 20日涨跌: {h['change_20d_pct']}%")
            print(f"  支撑: {h['support']} | 阻力: {h['resistance']}")
            print(f"  持仓: {h['shares']}股 | 市值: {h['market_value']}元 | 盈亏: {h['pnl']}元 ({h['pnl_pct']}%)")
        else:
            print(f"\n{h['name']}: 分析失败 - {h['error']}")
    
    print("\n" + "=" * 60)
    print("候选标的分析摘要")
    print("=" * 60)
    for c in candidates_analysis:
        if "error" not in c:
            print(f"\n{c['name']} ({c.get('original_code', 'N/A')})")
            print(f"  当前价: {c['current_price']} | RSI: {c['rsi']} ({c['rsi_status']})")
            print(f"  趋势: {c['trend']} | MACD: {c['macd_interpretation']}")
            print(f"  5日涨跌: {c['change_5d_pct']}% | 20日涨跌: {c['change_20d_pct']}%")
            print(f"  支撑 (建议买入): {c['support']} | 阻力 (目标价): {c['resistance']}")
        else:
            print(f"\n{c['name']}: 分析失败 - {c['error']}")

if __name__ == "__main__":
    main()

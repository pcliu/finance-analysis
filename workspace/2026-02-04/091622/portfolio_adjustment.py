#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Portfolio Adjustment Analysis - 2026-02-04
持仓调整分析 - 综合技术面诊断
"""

import sys
import os
import json
from datetime import datetime

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_macd,
    calculate_sma
)
from scripts.utils import make_serializable

# Current holdings from screenshot
CURRENT_HOLDINGS = {
    "510150": {"name": "消费ETF", "shares": 38000, "cost": 0.5490},
    "510880": {"name": "红利ETF", "shares": 10000, "cost": 3.0510},
    "512170": {"name": "医疗ETF", "shares": 14000, "cost": 0.3540},
    "512660": {"name": "军工ETF", "shares": 8000, "cost": 1.4830},
    "515050": {"name": "5GETF", "shares": 1000, "cost": 2.3750},
    "515070": {"name": "AI智能", "shares": 400, "cost": 2.0700},
    "515790": {"name": "光伏ETF", "shares": 1000, "cost": 1.1220},
    "588000": {"name": "科创50", "shares": 1000, "cost": 1.5480},
    "159241": {"name": "航空TH", "shares": 8000, "cost": 1.5100},
    "159770": {"name": "机器人AI", "shares": 200, "cost": 1.1070}
}

# Watchlist from ETFs.csv
WATCHLIST = {
    "159985": "豆粕ETF",
 "512890": "红利低波ETF",
    "159206": "卫星ETF",
    "516780": "稀土ETF",
    "561330": "矿业ETF",
    "159870": "化工ETF",
    "561560": "电力ETF",
    "159830": "上海金ETF",
    "518880": "黄金ETF",
    "512400": "有色金属ETF",
    "513180": "恒生科技指数ETF",
    "513630": "港股红利指数ETF",
    "159326": "电网设备ETF",
    "159516": "半导体设备ETF",
    "161226": "国投白银LOF"
}

def analyze_stock(ticker, name, period='3mo'):
    """Analyze single stock with comprehensive technical indicators"""
    try:
        print(f"分析 {name} ({ticker})...")
        
        # Fetch data
        data = fetch_stock_data(ticker, period=period)
        if data is None or len(data) < 50:
            print(f"  ⚠️ {name} 数据不足")
            return None
        
        # Calculate indicators
        rsi_6 = calculate_rsi(data, window=6)
        rsi_14 = calculate_rsi(data, window=14)
        bb = calculate_bollinger_bands(data, window=20)
        macd = calculate_macd(data)
        sma_20 = calculate_sma(data, window=20)
        sma_60 = calculate_sma(data, window=60)
        
        # Get latest values
        latest = data.iloc[-1]
        prev_close = data.iloc[-2]['Close'] if len(data) > 1 else latest['Close']
        
        # Calculate %B (position within Bollinger Bands)
        bb_range = bb['Upper'].iloc[-1] - bb['Lower'].iloc[-1]
        percent_b = (latest['Close'] - bb['Lower'].iloc[-1]) / bb_range if bb_range > 0 else 0.5
        
        # Calculate volume ratio
        avg_volume_20 = data['Volume'].iloc[-20:].mean()
        volume_ratio = latest['Volume'] / avg_volume_20 if avg_volume_20 > 0 else 1.0
        
        # Calculate 20-day return
        price_20_days_ago = data.iloc[-20]['Close'] if len(data) >= 20 else data.iloc[0]['Close']
        return_20d = (latest['Close'] - price_20_days_ago) / price_20_days_ago * 100
        
        # Daily change
        daily_change = (latest['Close'] - prev_close) / prev_close * 100
        
        result = {
            "ticker": ticker,
            "name": name,
            "price": latest['Close'],
            "daily_change": daily_change,
            "return_20d": return_20d,
            "rsi_6": rsi_6['RSI'].iloc[-1],
            "rsi_14": rsi_14['RSI'].iloc[-1],
            "macd": macd['MACD'].iloc[-1],
            "macd_signal": macd['Signal'].iloc[-1],
            "macd_hist": macd['Histogram'].iloc[-1],
            "bb_upper": bb['Upper'].iloc[-1],
            "bb_middle": bb['Middle'].iloc[-1],
            "bb_lower": bb['Lower'].iloc[-1],
            "percent_b": percent_b,
            "sma_20": sma_20['SMA'].iloc[-1],
            "sma_60": sma_60['SMA'].iloc[-1],
            "volume": latest['Volume'],
            "volume_ratio": volume_ratio,
            "date": str(latest.name.date())
        }
        
        print(f"  ✅ {name}: 价格={result['price']:.3f}, RSI(6)={result['rsi_6']:.2f}, %B={result['percent_b']:.2f}")
        return result
        
    except Exception as e:
        print(f"  ❌ {name} 分析失败: {str(e)}")
        return None

def main():
    """Main analysis workflow"""
    print("=" * 80)
    print("持仓调整分析 - Portfolio Adjustment Analysis")
    print(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    results = {
        "analysis_date": datetime.now().strftime('%Y-%m-%d'),
        "holdings": {},
        "watchlist": {},
        "summary": {}
    }
    
    # Analyze current holdings
    print("\n📊 分析当前持仓...")
    print("-" * 80)
    for ticker, info in CURRENT_HOLDINGS.items():
        analysis = analyze_stock(ticker, info['name'])
        if analysis:
            analysis['shares'] = info['shares']
            analysis['cost'] = info['cost']
            analysis['market_value'] = analysis['price'] * info['shares']
            analysis['profit_loss'] = (analysis['price'] - info['cost']) * info['shares']
            analysis['profit_loss_pct'] = (analysis['price'] - info['cost']) / info['cost'] * 100
            results['holdings'][ticker] = analysis
    
    # Analyze watchlist
    print("\n\n🔍 分析观察标的...")
    print("-" * 80)
    for ticker, name in WATCHLIST.items():
        analysis = analyze_stock(ticker, name)
        if analysis:
            results['watchlist'][ticker] = analysis
    
    # Calculate portfolio summary
    print("\n\n💼 组合汇总...")
    print("-" * 80)
    total_market_value = sum(h['market_value'] for h in results['holdings'].values())
    total_profit_loss = sum(h['profit_loss'] for h in results['holdings'].values())
    
    # Available cash from screenshot
    available_cash = 7994.98
    total_assets = total_market_value + available_cash
    
    results['summary'] = {
        "total_market_value": total_market_value,
        "total_profit_loss": total_profit_loss,
        "total_assets": total_assets,
        "available_cash": available_cash,
        "position_ratio": total_market_value / total_assets * 100,
        "holdings_count": len(results['holdings']),
        "watchlist_count": len(results['watchlist'])
    }
    
    print(f"持仓市值: {total_market_value:,.2f} 元")
    print(f"浮动盈亏: {total_profit_loss:,.2f} 元 ({total_profit_loss/total_market_value*100:.2f}%)")
    print(f"可用资金: {available_cash:,.2f} 元")
    print(f"总资产: {total_assets:,.2f} 元")
    print(f"仓位: {results['summary']['position_ratio']:.2f}%")
    
    # Save results
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(results), f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ 数据已保存到: {output_file}")
    print("=" * 80)
    
    return results

if __name__ == "__main__":
    main()

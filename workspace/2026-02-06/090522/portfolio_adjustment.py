#!/usr/bin/env python3
"""
持仓调整分析脚本
日期: 2026-02-06
覆盖: 10个持仓 + 15个候选标的（共25个ETF）
"""

import sys
import os
import json
from datetime import datetime

# 设置脚本目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# 定义所有关注的ETF
ETF_LIST = [
    # 当前持仓（10个）
    {"code": "510150", "name": "消费ETF", "holding": True, "shares": 38000, "cost": 0.5559},
    {"code": "510880", "name": "红利ETF", "holding": True, "shares": 10000, "cost": 3.0671},
    {"code": "512170", "name": "医疗ETF", "holding": True, "shares": 14000, "cost": 0.3585},
    {"code": "512660", "name": "军工ETF", "holding": True, "shares": 8000, "cost": 1.5128},
    {"code": "515050", "name": "5GETF", "holding": True, "shares": 1000, "cost": 2.3200},
    {"code": "515070", "name": "AI智能", "holding": True, "shares": 400, "cost": 1.9388},
    {"code": "515790", "name": "光伏ETF", "holding": True, "shares": 1000, "cost": 1.1005},
    {"code": "588000", "name": "科创50", "holding": True, "shares": 1000, "cost": 0.3019},
    {"code": "159241", "name": "航空TH", "holding": True, "shares": 8000, "cost": 1.5185},
    {"code": "159770", "name": "机器人AI", "holding": True, "shares": 200, "cost": 0.7670},
    
    # ETFs.csv中的候选标的（15个未持仓品种）
    {"code": "159985", "name": "豆粕ETF", "holding": False},
    {"code": "512890", "name": "红利低波ETF", "holding": False},
    {"code": "159206", "name": "卫星ETF", "holding": False},
    {"code": "516780", "name": "稀土ETF", "holding": False},
    {"code": "561330", "name": "矿业ETF", "holding": False},
    {"code": "159870", "name": "化工ETF", "holding": False},
    {"code": "561560", "name": "电力ETF", "holding": False},
    {"code": "159830", "name": "上海金ETF", "holding": False},
    {"code": "159326", "name": "电网设备ETF", "holding": False},
    {"code": "159516", "name": "半导体设备ETF", "holding": False},
    {"code": "161226", "name": "国投白银LOF", "holding": False},
    {"code": "518880", "name": "黄金ETF", "holding": False},
    {"code": "512400", "name": "有色金属ETF", "holding": False},
    {"code": "513180", "name": "恒生科技ETF", "holding": False},
    {"code": "513630", "name": "港股红利ETF", "holding": False},
]


def analyze_etf(etf_info):
    """分析单个ETF的技术指标"""
    code = etf_info["code"]
    name = etf_info["name"]
    
    try:
        # 获取6个月日线数据
        data = fetch_stock_data(code, period='6mo')
        
        if data is None or data.empty:
            print(f"警告: {name}({code}) 无法获取数据")
            return None
        
        # 计算技术指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        
        # 获取最新值
        current_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2])
        daily_change = (current_price - prev_price) / prev_price * 100
        
        # RSI
        current_rsi = float(rsi_df['RSI'].iloc[-1])
        
        # MACD
        macd_line = float(macd_df['MACD'].iloc[-1])
        signal_line = float(macd_df['Signal'].iloc[-1])
        histogram = float(macd_df['Histogram'].iloc[-1])
        
        # 判断MACD金叉/死叉
        prev_histogram = float(macd_df['Histogram'].iloc[-2])
        if histogram > 0 and prev_histogram <= 0:
            macd_signal = "金叉"
        elif histogram < 0 and prev_histogram >= 0:
            macd_signal = "死叉"
        elif histogram > 0:
            macd_signal = "金叉延续"
        else:
            macd_signal = "死叉延续"
        
        # 布林带 %B
        upper = float(bb_df['Upper'].iloc[-1])
        lower = float(bb_df['Lower'].iloc[-1])
        pct_b = (current_price - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
        
        # 成交量比（当前成交量/20日均量）
        vol_20_mean = float(data['Volume'].iloc[-20:].mean())
        current_vol = float(data['Volume'].iloc[-1])
        vol_ratio = current_vol / vol_20_mean if vol_20_mean > 0 else 1.0
        
        # 计算20日涨跌幅
        price_20d_ago = float(data['Close'].iloc[-20]) if len(data) >= 20 else float(data['Close'].iloc[0])
        pct_20d = (current_price - price_20d_ago) / price_20d_ago * 100
        
        result = {
            "code": code,
            "name": name,
            "holding": etf_info.get("holding", False),
            "shares": etf_info.get("shares", 0),
            "cost": etf_info.get("cost", 0),
            "current_price": round(current_price, 4),
            "daily_change": round(daily_change, 2),
            "pct_20d": round(pct_20d, 2),
            "rsi": round(current_rsi, 2),
            "macd": round(macd_line, 4),
            "macd_signal": round(signal_line, 4),
            "macd_histogram": round(histogram, 4),
            "macd_status": macd_signal,
            "pct_b": round(pct_b, 2),
            "bb_upper": round(upper, 4),
            "bb_lower": round(lower, 4),
            "vol_ratio": round(vol_ratio, 2),
        }
        
        # 添加持仓盈亏信息
        if etf_info.get("holding", False) and etf_info.get("cost", 0) > 0:
            cost = etf_info["cost"]
            shares = etf_info["shares"]
            profit = (current_price - cost) * shares
            profit_pct = (current_price - cost) / cost * 100
            result["profit"] = round(profit, 2)
            result["profit_pct"] = round(profit_pct, 2)
            result["market_value"] = round(current_price * shares, 2)
        
        print(f"✓ {name}({code}): RSI={current_rsi:.1f}, MACD={macd_signal}, 日涨跌={daily_change:+.2f}%")
        return result
        
    except Exception as e:
        print(f"✗ {name}({code}): 分析失败 - {str(e)}")
        return None


def main():
    print("=" * 60)
    print(f"持仓调整分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    print(f"\n分析标的: {len(ETF_LIST)}个ETF")
    print("-" * 60)
    
    # 分析所有ETF
    results = []
    holdings = []
    candidates = []
    
    for etf in ETF_LIST:
        result = analyze_etf(etf)
        if result:
            results.append(result)
            if result["holding"]:
                holdings.append(result)
            else:
                candidates.append(result)
    
    print("-" * 60)
    print(f"分析完成: 成功{len(results)}个, 失败{len(ETF_LIST)-len(results)}个")
    
    # 计算组合统计
    total_market_value = sum(h.get("market_value", 0) for h in holdings)
    total_profit = sum(h.get("profit", 0) for h in holdings)
    
    # 统计MACD状态
    golden_cross = [r for r in results if "金叉" in r.get("macd_status", "")]
    death_cross = [r for r in results if "死叉" in r.get("macd_status", "")]
    oversold = [r for r in results if r.get("rsi", 50) < 40]
    overbought = [r for r in results if r.get("rsi", 50) > 70]
    
    summary = {
        "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M'),
        "total_etfs": len(results),
        "holdings_count": len(holdings),
        "candidates_count": len(candidates),
        "total_market_value": round(total_market_value, 2),
        "total_profit": round(total_profit, 2),
        "golden_cross_count": len(golden_cross),
        "death_cross_count": len(death_cross),
        "oversold_count": len(oversold),
        "overbought_count": len(overbought),
        "golden_cross_etfs": [f"{r['name']}({r['code']})" for r in golden_cross],
        "oversold_etfs": [f"{r['name']}({r['code']}) RSI={r['rsi']}" for r in oversold],
        "overbought_etfs": [f"{r['name']}({r['code']}) RSI={r['rsi']}" for r in overbought],
    }
    
    # 输出汇总
    print("\n" + "=" * 60)
    print("市场概览")
    print("=" * 60)
    print(f"金叉品种: {len(golden_cross)}个 ({len(golden_cross)/len(results)*100:.0f}%)")
    print(f"死叉品种: {len(death_cross)}个 ({len(death_cross)/len(results)*100:.0f}%)")
    print(f"超卖品种(RSI<40): {len(oversold)}个")
    print(f"超买品种(RSI>70): {len(overbought)}个")
    
    if golden_cross:
        print(f"\n金叉品种列表:")
        for r in golden_cross:
            print(f"  - {r['name']}({r['code']}): RSI={r['rsi']}, %B={r['pct_b']}")
    
    if oversold:
        print(f"\n超卖品种列表:")
        for r in oversold:
            print(f"  - {r['name']}({r['code']}): RSI={r['rsi']}, %B={r['pct_b']}")
    
    if overbought:
        print(f"\n超买品种列表:")
        for r in overbought:
            print(f"  - {r['name']}({r['code']}): RSI={r['rsi']}, %B={r['pct_b']}")
    
    # 组装完整结果
    full_results = {
        "summary": summary,
        "holdings": sorted(holdings, key=lambda x: x.get("rsi", 50), reverse=True),
        "candidates": sorted(candidates, key=lambda x: x.get("rsi", 50), reverse=True),
        "all_results": results,
    }
    
    # 保存到JSON
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(full_results), f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存: {output_file}")
    return full_results


if __name__ == "__main__":
    main()

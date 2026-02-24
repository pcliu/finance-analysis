#!/usr/bin/env python3
"""
持仓调整技术分析脚本
生成时间: 2026-02-05 08:55
"""
import sys
import os
import json
from datetime import datetime, timedelta

# Robust Import
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# 定义所有标的
HOLDINGS = [
    ("510150", "消费ETF", 38000, 0.5559),
    ("510880", "红利ETF", 10000, 3.0671),
    ("512170", "医疗ETF", 14000, 0.3585),
    ("512660", "军工ETF", 8000, 1.5128),
    ("515050", "5GETF", 1000, 2.3200),
    ("515070", "AI智能ETF", 400, 1.9388),
    ("515790", "光伏ETF", 1000, 1.1005),
    ("588000", "科创50", 1000, 0.3019),
    ("159241", "航空TH", 8000, 1.5185),
    ("159770", "机器人AI", 200, 0.7670),
]

# ETFs.csv中所有关注标的
WATCHLIST = [
    ("159985", "豆粕ETF"),
    ("512890", "红利低波ETF"),
    ("159206", "卫星ETF"),
    ("516780", "稀土ETF"),
    ("561330", "矿业ETF"),
    ("159870", "化工ETF"),
    ("561560", "电力ETF"),
    ("159830", "上海金ETF"),
    ("159326", "电网设备ETF"),
    ("159516", "半导体设备ETF"),
    ("161226", "国投白银LOF"),
    ("518880", "黄金ETF"),
    ("512400", "有色金属ETF"),
    ("513180", "恒生科技ETF"),
    ("513630", "港股红利ETF"),
]

def analyze_single_etf(code, name, period='6mo'):
    """分析单个ETF的技术指标"""
    try:
        data = fetch_stock_data(code, period=period)
        if data is None or len(data) < 30:
            print(f"警告: {code} {name} 数据不足")
            return None
        
        # 计算技术指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        
        # 计算成交量比率
        if 'Volume' in data.columns:
            vol_20_avg = data['Volume'].rolling(20).mean()
            vol_ratio = data['Volume'].iloc[-1] / vol_20_avg.iloc[-1] if vol_20_avg.iloc[-1] > 0 else 1.0
        else:
            vol_ratio = 1.0
        
        # 获取最新值
        latest_close = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2]) if len(data) > 1 else latest_close
        daily_change = (latest_close - prev_close) / prev_close * 100
        
        rsi = float(rsi_df['RSI'].iloc[-1])
        macd_line = float(macd_df['MACD'].iloc[-1])
        signal_line = float(macd_df['Signal'].iloc[-1])
        macd_hist = float(macd_df['Histogram'].iloc[-1])
        macd_cross = "金叉" if macd_line > signal_line else "死叉"
        
        bb_upper = float(bb_df['Upper'].iloc[-1])
        bb_lower = float(bb_df['Lower'].iloc[-1])
        bb_middle = float(bb_df['Middle'].iloc[-1])
        percent_b = (latest_close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) > 0 else 0.5
        
        # 计算20日涨幅
        close_20_ago = float(data['Close'].iloc[-20]) if len(data) >= 20 else float(data['Close'].iloc[0])
        change_20d = (latest_close - close_20_ago) / close_20_ago * 100
        
        return {
            'code': code,
            'name': name,
            'close': latest_close,
            'daily_change': daily_change,
            'change_20d': change_20d,
            'rsi': rsi,
            'macd_line': macd_line,
            'signal_line': signal_line,
            'macd_hist': macd_hist,
            'macd_cross': macd_cross,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'percent_b': percent_b,
            'volume_ratio': vol_ratio,
        }
    except Exception as e:
        print(f"错误: 分析 {code} {name} 失败 - {e}")
        return None

def main():
    print("=" * 60)
    print("持仓调整技术分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        'generated_at': datetime.now().isoformat(),
        'holdings': [],
        'watchlist': [],
    }
    
    # 分析持仓
    print("\n【持仓分析】")
    print("-" * 40)
    for code, name, shares, cost in HOLDINGS:
        print(f"分析 {code} {name}...")
        analysis = analyze_single_etf(code, name)
        if analysis:
            analysis['shares'] = shares
            analysis['cost'] = cost
            analysis['market_value'] = shares * analysis['close']
            analysis['profit_loss'] = (analysis['close'] - cost) * shares
            analysis['profit_loss_pct'] = (analysis['close'] - cost) / cost * 100
            results['holdings'].append(analysis)
            print(f"  → RSI={analysis['rsi']:.2f}, MACD={analysis['macd_cross']}, %B={analysis['percent_b']:.2f}")
    
    # 分析观察列表
    print("\n【观察列表分析】")
    print("-" * 40)
    for code, name in WATCHLIST:
        print(f"分析 {code} {name}...")
        analysis = analyze_single_etf(code, name)
        if analysis:
            results['watchlist'].append(analysis)
            print(f"  → RSI={analysis['rsi']:.2f}, MACD={analysis['macd_cross']}, %B={analysis['percent_b']:.2f}")
    
    # 保存结果
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    clean_results = make_serializable(results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n数据已保存至: {output_file}")
    
    # 打印汇总
    print("\n" + "=" * 60)
    print("技术分析汇总")
    print("=" * 60)
    
    print("\n【持仓技术状态】")
    print(f"{'名称':<12} {'现价':>8} {'日涨跌':>8} {'RSI':>6} {'MACD':>6} {'%B':>6}")
    print("-" * 52)
    for h in results['holdings']:
        print(f"{h['name']:<12} {h['close']:>8.3f} {h['daily_change']:>7.2f}% {h['rsi']:>6.2f} {h['macd_cross']:>6} {h['percent_b']:>6.2f}")
    
    print("\n【观察列表技术状态】")
    print(f"{'名称':<12} {'现价':>8} {'日涨跌':>8} {'RSI':>6} {'MACD':>6} {'%B':>6}")
    print("-" * 52)
    for w in results['watchlist']:
        print(f"{w['name']:<12} {w['close']:>8.3f} {w['daily_change']:>7.2f}% {w['rsi']:>6.2f} {w['macd_cross']:>6} {w['percent_b']:>6.2f}")
    
    # 统计
    all_items = results['holdings'] + results['watchlist']
    golden_cross = [x for x in all_items if x['macd_cross'] == '金叉']
    oversold = [x for x in all_items if x['rsi'] < 40]
    overbought = [x for x in all_items if x['rsi'] > 70]
    
    print(f"\n【统计】")
    print(f"- 总标的数: {len(all_items)}")
    print(f"- MACD金叉: {len(golden_cross)} ({len(golden_cross)/len(all_items)*100:.1f}%)")
    print(f"- RSI超卖(<40): {len(oversold)}")
    print(f"- RSI超买(>70): {len(overbought)}")
    
    return results

if __name__ == "__main__":
    main()

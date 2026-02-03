#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓调整分析脚本
生成日期: 2026-02-02 09:10
"""

import sys
import os
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Robust Import
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data,
    calculate_rsi,
    calculate_bollinger_bands,
    calculate_macd,
    calculate_sma,
    calculate_ema,
    RiskManager
)
from scripts.utils import make_serializable

# 输出路径 - 使用 __file__ 确保和脚本在同一目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 当前持仓（根据用户截图）
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 33000, 'cost': 0.5480},
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 3.1440},
    '512170': {'name': '医疗ETF', 'shares': 10000, 'cost': 0.3560},
    '512660': {'name': '军工ETF', 'shares': 6000, 'cost': 1.4460},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.3850},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 2.1180},
    '515790': {'name': '光伏ETF', 'shares': 1000, 'cost': 1.0680},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 1.5880},
    '159241': {'name': '航空TH', 'shares': 6000, 'cost': 1.4560},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 1.1010},
}

# ETF候选池（从ETFs.csv读取）
ETF_WATCHLIST = {
    '510150': '消费ETF',
    '159985': '豆粕ETF',
    '512890': '红利低波ETF',
    '512660': '军工ETF',
    '159241': '航空航天ETF天弘',
    '159206': '卫星ETF',
    '515790': '光伏ETF',
    '516780': '稀土ETF',
    '512170': '医疗ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159770': '机器人ETF',
    '515070': '人工智能AIETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '515050': '通信ETF华夏',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '510880': '红利ETF',
    '513180': '恒生科技指数ETF',
    '513630': '港股红利指数ETF',
    '588000': '科创50ETF',
}

def analyze_etf(code, name, period='6mo'):
    """
    分析单个ETF的技术指标
    """
    try:
        print(f"正在分析 {name} ({code})...")
        
        # 获取数据
        data = fetch_stock_data(code, period=period)
        
        if data is None or len(data) < 50:
            print(f"  ⚠️  数据不足，跳过")
            return None
        
        # 计算技术指标
        rsi_6 = calculate_rsi(data, window=6)
        rsi_14 = calculate_rsi(data, window=14)
        bb = calculate_bollinger_bands(data, window=20, num_std=2)
        macd = calculate_macd(data)
        sma_20 = calculate_sma(data, window=20)
        sma_60 = calculate_sma(data, window=60)
        
        # 获取最新值
        latest = {
            'code': code,
            'name': name,
            'price': float(data['Close'].iloc[-1]),
            'prev_price': float(data['Close'].iloc[-2]),
            'volume': float(data['Volume'].iloc[-1]),
            'avg_volume': float(data['Volume'].iloc[-20:].mean()),
            'rsi_6': float(rsi_6['RSI'].iloc[-1]),
            'rsi_14': float(rsi_14['RSI'].iloc[-1]),
            'rsi_6_prev': float(rsi_6['RSI'].iloc[-2]),
            'bb_upper': float(bb['Upper'].iloc[-1]),
            'bb_middle': float(bb['Middle'].iloc[-1]),
            'bb_lower': float(bb['Lower'].iloc[-1]),
            'bb_pct_b': float(bb['Percent_B'].iloc[-1]),
            'macd': float(macd['MACD'].iloc[-1]),
            'macd_signal': float(macd['Signal'].iloc[-1]),
            'macd_hist': float(macd['Histogram'].iloc[-1]),
            'macd_hist_prev': float(macd['Histogram'].iloc[-2]),
            'sma_20': float(sma_20['SMA'].iloc[-1]),
            'sma_60': float(sma_60['SMA'].iloc[-1]),
        }
        
        # 计算衍生指标
        latest['change_pct'] = ((latest['price'] - latest['prev_price']) / latest['prev_price']) * 100
        latest['volume_ratio'] = latest['volume'] / latest['avg_volume'] if latest['avg_volume'] > 0 else 1
        latest['price_to_sma20'] = (latest['price'] / latest['sma_20'] - 1) * 100 if latest['sma_20'] > 0 else 0
        latest['price_to_sma60'] = (latest['price'] / latest['sma_60'] - 1) * 100 if latest['sma_60'] > 0 else 0
        
        # 计算20日涨幅
        if len(data) >= 20:
            price_20d_ago = float(data['Close'].iloc[-20])
            latest['change_20d'] = ((latest['price'] - price_20d_ago) / price_20d_ago) * 100
        else:
            latest['change_20d'] = 0
        
        # MACD趋势判断
        latest['macd_trend'] = 'golden_cross' if latest['macd'] > latest['macd_signal'] and latest['macd_hist_prev'] <= 0 else \
                               'bullish' if latest['macd'] > latest['macd_signal'] else \
                               'death_cross' if latest['macd'] < latest['macd_signal'] and latest['macd_hist_prev'] >= 0 else \
                               'bearish'
        
        print(f"  ✓ {name}: 价格={latest['price']:.3f}, RSI(6)={latest['rsi_6']:.2f}, %B={latest['bb_pct_b']:.2f}")
        
        return latest
        
    except Exception as e:
        print(f"  ✗ 分析 {name} 时出错: {str(e)}")
        return None

def main():
    print("="*80)
    print("持仓调整分析 - 2026-02-02 周日")
    print("="*80)
    print()
    
    # 分析所有ETF
    all_analysis = {}
    
    # 合并持仓和观察列表（去重）
    all_etfs = dict(ETF_WATCHLIST)
    
    for code, name in all_etfs.items():
        result = analyze_etf(code, name)
        if result:
            all_analysis[code] = result
    
    print()
    print(f"分析完成，共获取 {len(all_analysis)} 个有效数据")
    print()
    
    # 保存原始数据
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(make_serializable({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'current_holdings': CURRENT_HOLDINGS,
            'analysis': all_analysis,
        }), f, indent=2, ensure_ascii=False)
    
    print(f"✓ 数据已保存到: {output_file}")
    
    # 输出关键摘要
    print()
    print("="*80)
    print("技术指标摘要")
    print("="*80)
    print()
    
    # 按RSI分类
    extreme_overbought = []  # RSI > 85
    overbought = []  # 70 < RSI <= 85
    healthy = []  # 40 <= RSI <= 70
    oversold = []  # 25 < RSI < 40
    extreme_oversold = []  # RSI <= 25
    
    for code, data in all_analysis.items():
        rsi = data['rsi_6']
        if rsi > 85:
            extreme_overbought.append((code, data))
        elif rsi > 70:
            overbought.append((code, data))
        elif rsi >= 40:
            healthy.append((code, data))
        elif rsi > 25:
            oversold.append((code, data))
        else:
            extreme_oversold.append((code, data))
    
    # 输出分类结果
    if extreme_overbought:
        print("🔴 极度超买区 (RSI > 85) - 绝对禁入:")
        for code, data in sorted(extreme_overbought, key=lambda x: x[1]['rsi_6'], reverse=True):
            held = "✓持仓" if code in CURRENT_HOLDINGS else "未持有"
            print(f"  {data['name']:12s} ({code}): RSI={data['rsi_6']:5.2f}, %B={data['bb_pct_b']:5.2f}, 涨跌={data['change_pct']:+6.2f}% [{held}]")
        print()
    
    if overbought:
        print("🟠 高位震荡区 (70 < RSI <= 85) - 警惕:")
        for code, data in sorted(overbought, key=lambda x: x[1]['rsi_6'], reverse=True):
            held = "✓持仓" if code in CURRENT_HOLDINGS else "未持有"
            print(f"  {data['name']:12s} ({code}): RSI={data['rsi_6']:5.2f}, %B={data['bb_pct_b']:5.2f}, 涨跌={data['change_pct']:+6.2f}% [{held}]")
        print()
    
    if healthy:
        print("✅ 健康趋势区 (40 <= RSI <= 70) - 核心持仓区:")
        for code, data in sorted(healthy, key=lambda x: x[1]['rsi_6'], reverse=True):
            held = "✓持仓" if code in CURRENT_HOLDINGS else "未持有"
            print(f"  {data['name']:12s} ({code}): RSI={data['rsi_6']:5.2f}, %B={data['bb_pct_b']:5.2f}, 涨跌={data['change_pct']:+6.2f}% [{held}]")
        print()
    
    if oversold:
        print("🟢 超卖区 (25 < RSI < 40) - 左侧建仓机会:")
        for code, data in sorted(oversold, key=lambda x: x[1]['rsi_6']):
            held = "✓持仓" if code in CURRENT_HOLDINGS else "未持有"
            print(f"  {data['name']:12s} ({code}): RSI={data['rsi_6']:5.2f}, %B={data['bb_pct_b']:5.2f}, 涨跌={data['change_pct']:+6.2f}% [{held}]")
        print()
    
    if extreme_oversold:
        print("🟢🟢 极度超卖区 (RSI <= 25) - 黄金深坑:")
        for code, data in sorted(extreme_oversold, key=lambda x: x[1]['rsi_6']):
            held = "✓持仓" if code in CURRENT_HOLDINGS else "未持有"
            print(f"  {data['name']:12s} ({code}): RSI={data['rsi_6']:5.2f}, %B={data['bb_pct_b']:5.2f}, 涨跌={data['change_pct']:+6.2f}% [{held}]")
        print()
    
    print("="*80)
    print("分析完成！接下来将生成详细报告...")
    print("="*80)

if __name__ == '__main__':
    main()

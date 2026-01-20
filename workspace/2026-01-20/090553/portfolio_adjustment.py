#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓调整分析 - 2026-01-20
基于当前持仓和ETFs.csv进行综合分析,生成调仓建议
"""

import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd
from scripts.utils import make_serializable

# 环境配置
ENV_PYTHON = "/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python"

# 当前持仓
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 10000, 'cost': 0.5670},
    '510880': {'name': '红利ETF', 'shares': 3500, 'cost': 3.1790},
    '512660': {'name': '军工ETF', 'shares': 5000, 'cost': 1.5260},
    '513180': {'name': '恒指科技', 'shares': 800, 'cost': 0.7600},
    '513630': {'name': '香港红利', 'shares': 500, 'cost': 1.6260},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.3670},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 2.1000},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 1.5860},
    '159241': {'name': '航空TH', 'shares': 5000, 'cost': 1.5400},
    '159770': {'name': '机器人AI', 'shares': 500, 'cost': 1.1490},
    '159830': {'name': '上海金', 'shares': 400, 'cost': 10.4260},
    '161226': {'name': '白银基金', 'shares': 300, 'cost': 3.3840},
}

# ETFs.csv中的所有品种
ALL_ETFS = {
    '510150': '消费 ETF',
    '512660': '军工 ETF',
    '159241': '航空航天 ETF 天弘',
    '159352': 'A500ETF 南方',
    '159830': '上海金 ETF',
    '159770': '机器人 ETF',
    '515070': '人工智能 AIETF',
    '159326': '电网设备 ETF',
    '159516': '半导体设备 ETF',
    '515050': '通信 ETF 华夏',
    '161226': '国投白银 LOF',
    '518880': '黄金 ETF',
    '512400': '有色金属 ETF',
    '510880': '红利 ETF',
    '513180': '恒生科技指数 ETF',
    '513630': '港股红利指数 ETF',
    '588000': '科创 50ETF',
}

def analyze_ticker(ticker, name):
    """分析单个标的的技术指标"""
    try:
        # 对于沪深ETF,需要加.SS或.SZ后缀
        symbol = ticker
        if ticker.startswith('5'):  # 上海
            symbol = ticker + '.SS'
        elif ticker.startswith('1'):  # 深圳
            symbol = ticker + '.SZ'
        
        data = fetch_stock_data(symbol, period='3mo')
        if data.empty:
            return None
        
        # 计算技术指标
        rsi_14 = calculate_rsi(data, window=14)
        rsi_6 = calculate_rsi(data, window=6)
        sma_20 = calculate_sma(data, window=20)
        macd = calculate_macd(data)
        
        current_price = float(data['Close'].iloc[-1])
        current_rsi_14 = float(rsi_14['RSI'].iloc[-1])
        current_rsi_6 = float(rsi_6['RSI'].iloc[-1])
        current_sma_20 = float(sma_20['SMA'].iloc[-1])
        
        # 计算涨跌幅
        price_20d_ago = float(data['Close'].iloc[-20]) if len(data) >= 20 else float(data['Close'].iloc[0])
        pct_change_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
        
        return {
            'ticker': ticker,
            'name': name,
            'price': current_price,
            'rsi_14': current_rsi_14,
            'rsi_6': current_rsi_6,
            'sma_20': current_sma_20,
            'macd': float(macd['MACD'].iloc[-1]),
            'macd_signal': float(macd['Signal'].iloc[-1]),
            'pct_change_20d': pct_change_20d,
        }
    except Exception as e:
        print(f"分析 {ticker} 时出错: {e}")
        return None

def generate_signal(analysis, is_holding=False, holding_info=None):
    """生成交易信号"""
    rsi_14 = analysis['rsi_14']
    rsi_6 = analysis['rsi_6']
    price = analysis['price']
    
    # 趋势判断
    if rsi_6 > 80:
        trend = "🚀 极强"
        trend_desc = "极度超买"
    elif rsi_6 > 70:
        trend = "📈 强势"
        trend_desc = "超买"
    elif rsi_6 > 60:
        trend = "↗️ 震荡上行"
        trend_desc = "偏强"
    elif rsi_6 > 40:
        trend = "➡️ 震荡"
        trend_desc = "中性"
    elif rsi_6 > 30:
        trend = "↘️ 回调"
        trend_desc = "偏弱"
    else:
        trend = "📉 弱势"
        trend_desc = "超卖"
    
    # 操作建议
    if is_holding:
        # 计算盈亏
        profit_pct = ((price - holding_info['cost']) / holding_info['cost']) * 100
        
        if rsi_6 > 80:
            action = "🔴 严重超买 - 建议减仓"
            reason = f"RSI(6)={rsi_6:.1f}严重超买,浮盈{profit_pct:.1f}%,建议止盈"
        elif rsi_6 > 70:
            action = "🟠 超买 - 观察或减仓"
            reason = f"RSI(6)={rsi_6:.1f}超买,浮盈{profit_pct:.1f}%,可分批减仓"
        elif rsi_6 < 30:
            action = "🟢 超卖 - 可考虑补仓"
            reason = f"RSI(6)={rsi_6:.1f}超卖,亏损{abs(profit_pct):.1f}%,防守性加仓"
        else:
            action = "✅ 持有"
            reason = f"趋势{trend_desc},浮盈{profit_pct:.1f}%,继续持有"
    else:
        # 非持仓品种
        if rsi_6 > 80:
            action = "❌ 严禁追高"
            reason = f"RSI(6)={rsi_6:.1f}严重过热,风险极大"
        elif rsi_6 > 70:
            action = "⚠️ 等待回调"
            reason = f"RSI(6)={rsi_6:.1f}超买,等待回调至50以下"
        elif rsi_6 < 30:
            action = "✅ 强烈推荐建仓"
            reason = f"RSI(6)={rsi_6:.1f}超卖,价格{price:.3f},黄金坑"
        elif rsi_6 < 40:
            action = "✅ 可建仓"
            reason = f"RSI(6)={rsi_6:.1f}相对低位,价格{price:.3f},性价比佳"
        else:
            action = "⏸️ 观望"
            reason = f"RSI(6)={rsi_6:.1f}中性偏高,等待更好时机"
    
    return {
        'trend': trend,
        'action': action,
        'reason': reason
    }

def main():
    print("="*80)
    print("开始持仓调整分析...")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'holdings': [],
        'non_holdings': [],
        'recommendations': {
            'sell': [],
            'hold': [],
            'buy': [],
        }
    }
    
    # 1. 分析当前持仓
    print("\n[1/2] 分析当前持仓...")
    for ticker, info in CURRENT_HOLDINGS.items():
        print(f"  - 分析 {ticker} ({info['name']})...")
        analysis = analyze_ticker(ticker, info['name'])
        if analysis:
            signal = generate_signal(analysis, is_holding=True, holding_info=info)
            analysis.update(signal)
            analysis['holding_info'] = info
            results['holdings'].append(analysis)
            
            # 分类建议
            if '减仓' in signal['action'] or '止盈' in signal['action']:
                results['recommendations']['sell'].append(analysis)
            else:
                results['recommendations']['hold'].append(analysis)
    
    # 2. 分析非持仓品种
    print("\n[2/2] 分析非持仓品种...")
    non_holding_tickers = set(ALL_ETFS.keys()) - set(CURRENT_HOLDINGS.keys())
    for ticker in non_holding_tickers:
        name = ALL_ETFS[ticker]
        print(f"  - 分析 {ticker} ({name})...")
        analysis = analyze_ticker(ticker, name)
        if analysis:
            signal = generate_signal(analysis, is_holding=False)
            analysis.update(signal)
            results['non_holdings'].append(analysis)
            
            # 分类建议
            if '建仓' in signal['action']:
                results['recommendations']['buy'].append(analysis)
    
    # 3. 按RSI排序
    results['holdings'].sort(key=lambda x: x['rsi_6'], reverse=True)
    results['non_holdings'].sort(key=lambda x: x['rsi_6'])
    results['recommendations']['sell'].sort(key=lambda x: x['rsi_6'], reverse=True)
    results['recommendations']['buy'].sort(key=lambda x: x['rsi_6'])
    
    # 4. 保存结果
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    clean_results = make_serializable(results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ 分析完成! 结果已保存至: {output_file}")
    print("="*80)
    
    # 5. 输出摘要
    print(f"\n📊 分析摘要:")
    print(f"  - 当前持仓品种: {len(results['holdings'])}")
    print(f"  - 需减仓品种: {len(results['recommendations']['sell'])}")
    print(f"  - 可建仓品种: {len(results['recommendations']['buy'])}")
    print(f"  - 非持仓分析品种: {len(results['non_holdings'])}")

if __name__ == '__main__':
    main()

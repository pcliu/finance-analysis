#!/usr/bin/env python3
"""
持仓调整分析脚本
基于当前持仓数据获取最新技术指标，生成仓位调整建议
"""

import sys
import os
import json
from datetime import datetime

# 获取脚本所在目录作为输出目录
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 添加skills路径
SKILL_PATH = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading'
sys.path.insert(0, SKILL_PATH)

from scripts import (
    fetch_stock_data,
    calculate_rsi,
    calculate_macd,
    calculate_sma,
    calculate_bollinger_bands,
)

# ============================================
# 当前持仓数据 (基于用户截图 2026-01-19)
# ============================================
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 5000, 'cost': 0.5751, 'current_price': 0.5680, 'market_value': 2840.00, 'weight': 3.02, 'pnl': 0.00, 'pnl_pct': 0.00},
    '510880': {'name': '红利ETF', 'shares': 2000, 'cost': 3.2020, 'current_price': 3.1580, 'market_value': 6316.00, 'weight': 6.71, 'pnl': -10.00, 'pnl_pct': -0.16},
    '512660': {'name': '军工ETF', 'shares': 5000, 'cost': 1.5264, 'current_price': 1.4870, 'market_value': 7435.00, 'weight': 7.90, 'pnl': -40.00, 'pnl_pct': -0.54},
    '513180': {'name': '恒指科技', 'shares': 800, 'cost': 0.7686, 'current_price': 0.7610, 'market_value': 608.80, 'weight': 0.65, 'pnl': -5.60, 'pnl_pct': -0.91},
    '513630': {'name': '香港红利', 'shares': 500, 'cost': 1.6180, 'current_price': 1.6240, 'market_value': 812.00, 'weight': 0.86, 'pnl': -5.00, 'pnl_pct': -0.61},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.3200, 'current_price': 2.3820, 'market_value': 2382.00, 'weight': 2.53, 'pnl': -24.00, 'pnl_pct': -1.00},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 1.9388, 'current_price': 2.1270, 'market_value': 850.80, 'weight': 0.90, 'pnl': -1.20, 'pnl_pct': -0.14},
    '588000': {'name': '科创50', 'shares': 2000, 'cost': 0.9502, 'current_price': 1.5870, 'market_value': 3174.00, 'weight': 3.37, 'pnl': -12.00, 'pnl_pct': -0.38},
    '159241': {'name': '航空TH', 'shares': 5000, 'cost': 1.5292, 'current_price': 1.4770, 'market_value': 7385.00, 'weight': 7.84, 'pnl': -45.00, 'pnl_pct': -0.61},
    '159770': {'name': '机器人AI', 'shares': 700, 'cost': 1.0407, 'current_price': 1.1480, 'market_value': 803.60, 'weight': 0.85, 'pnl': 2.10, 'pnl_pct': 0.26},
    '159830': {'name': '上海金', 'shares': 400, 'cost': 9.7220, 'current_price': 10.3920, 'market_value': 4156.80, 'weight': 4.42, 'pnl': 49.20, 'pnl_pct': 1.20},
    '161226': {'name': '白银基金', 'shares': 300, 'cost': 2.1530, 'current_price': 3.0940, 'market_value': 928.20, 'weight': 0.99, 'pnl': 0.00, 'pnl_pct': 0.00},
}

# 计算总市值和现金估算
total_market_value = sum(h['market_value'] for h in CURRENT_HOLDINGS.values())
# 基于权重推算总资产 (使用权重反推)
# 总资产 ≈ 总市值 / 总权重
total_weight = sum(h['weight'] for h in CURRENT_HOLDINGS.values())  # 约40%
estimated_total_assets = total_market_value / (total_weight / 100) if total_weight > 0 else total_market_value
estimated_cash = estimated_total_assets - total_market_value

print(f"=== 持仓调整分析 ===")
print(f"分析日期: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"持仓总市值: ¥{total_market_value:,.2f}")
print(f"估算总资产: ¥{estimated_total_assets:,.2f}")
print(f"估算可用现金: ¥{estimated_cash:,.2f}")
print(f"资金利用率: {total_weight:.2f}%")
print()

# ============================================
# 获取技术指标
# ============================================
def analyze_etf(ticker: str, name: str) -> dict:
    """分析单个ETF的技术指标"""
    try:
        # A股ETF需要添加交易所后缀
        if ticker.startswith('51') or ticker.startswith('58'):
            yahoo_ticker = f"{ticker}.SS"  # 上海
        elif ticker.startswith('1'):
            yahoo_ticker = f"{ticker}.SZ"  # 深圳
        else:
            yahoo_ticker = ticker
        
        data = fetch_stock_data(yahoo_ticker, period='3mo')
        
        if data is None or data.empty:
            return {'ticker': ticker, 'name': name, 'error': '数据获取失败'}
        
        # 计算技术指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        sma_20_df = calculate_sma(data, window=20)
        sma_60_df = calculate_sma(data, window=60)
        bb_df = calculate_bollinger_bands(data)
        
        # 获取最新值
        latest_close = data['Close'].iloc[-1]
        latest_rsi = rsi_df['RSI'].iloc[-1] if 'RSI' in rsi_df.columns else None
        latest_macd = macd_df['MACD'].iloc[-1] if 'MACD' in macd_df.columns else None
        latest_signal = macd_df['Signal'].iloc[-1] if 'Signal' in macd_df.columns else None
        latest_sma20 = sma_20_df['SMA'].iloc[-1] if 'SMA' in sma_20_df.columns else None
        latest_sma60 = sma_60_df['SMA'].iloc[-1] if 'SMA' in sma_60_df.columns else None
        
        # 布林带
        bb_upper = bb_df['Upper'].iloc[-1] if 'Upper' in bb_df.columns else None
        bb_middle = bb_df['Middle'].iloc[-1] if 'Middle' in bb_df.columns else None
        bb_lower = bb_df['Lower'].iloc[-1] if 'Lower' in bb_df.columns else None
        
        # 计算5日涨跌幅
        if len(data) >= 5:
            change_5d = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100
        else:
            change_5d = 0
        
        # 计算20日涨跌幅
        if len(data) >= 20:
            change_20d = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
        else:
            change_20d = 0
        
        # 趋势判断
        trend = "Neutral"
        if latest_sma20 and latest_sma60:
            if latest_sma20 > latest_sma60 and latest_close > latest_sma20:
                trend = "Bullish"
            elif latest_sma20 < latest_sma60 and latest_close < latest_sma20:
                trend = "Bearish"
            elif latest_sma20 > latest_sma60:
                trend = "Weakening"
            elif latest_sma20 < latest_sma60:
                trend = "Recovering"
        
        return {
            'ticker': ticker,
            'name': name,
            'price': float(latest_close),
            'rsi': float(latest_rsi) if latest_rsi else None,
            'macd': float(latest_macd) if latest_macd else None,
            'macd_signal': float(latest_signal) if latest_signal else None,
            'sma20': float(latest_sma20) if latest_sma20 else None,
            'sma60': float(latest_sma60) if latest_sma60 else None,
            'bb_upper': float(bb_upper) if bb_upper else None,
            'bb_middle': float(bb_middle) if bb_middle else None,
            'bb_lower': float(bb_lower) if bb_lower else None,
            'change_5d': float(change_5d),
            'change_20d': float(change_20d),
            'trend': trend,
            'error': None
        }
    except Exception as e:
        return {'ticker': ticker, 'name': name, 'error': str(e)}

print(">>> 正在获取持仓ETF技术指标...")
print()

holdings_analysis = []
for ticker, info in CURRENT_HOLDINGS.items():
    print(f"  分析 {info['name']} ({ticker})...")
    result = analyze_etf(ticker, info['name'])
    result.update({
        'shares': info['shares'],
        'cost': info['cost'],
        'market_value': info['market_value'],
        'weight': info['weight'],
        'holding_pnl': info['pnl'],
        'holding_pnl_pct': info['pnl_pct']
    })
    holdings_analysis.append(result)

print()
print(">>> 技术指标分析完成")
print()

# ============================================
# 生成操作建议
# ============================================
recommendations = {
    'sell': [],      # 建议卖出
    'reduce': [],    # 建议减持
    'hold': [],      # 建议持有
    'add': [],       # 建议加仓
    'buy': [],       # 建议建仓 (新品种)
}

def generate_recommendation(analysis: dict) -> dict:
    """根据技术指标生成操作建议"""
    ticker = analysis['ticker']
    name = analysis['name']
    rsi = analysis.get('rsi')
    trend = analysis.get('trend', 'Neutral')
    change_5d = analysis.get('change_5d', 0)
    change_20d = analysis.get('change_20d', 0)
    macd = analysis.get('macd')
    macd_signal = analysis.get('macd_signal')
    price = analysis.get('price')
    shares = analysis.get('shares', 0)
    weight = analysis.get('weight', 0)
    cost = analysis.get('cost', 0)
    
    # 计算持仓盈亏
    if price and cost:
        profit_pct = (price - cost) / cost * 100
    else:
        profit_pct = 0
    
    action = 'hold'
    reasons = []
    target_shares = shares
    urgency = 'low'  # low, medium, high
    
    if analysis.get('error'):
        return {
            'ticker': ticker,
            'name': name,
            'action': 'hold',
            'action_cn': '持有',
            'target_shares': shares,
            'delta_shares': 0,
            'reasons': [f"数据获取失败: {analysis['error']}"],
            'urgency': 'low'
        }
    
    # RSI超买超卖判断
    if rsi:
        if rsi >= 80:
            action = 'sell'
            reasons.append(f"RSI={rsi:.1f} 严重超买")
            urgency = 'high'
        elif rsi >= 70:
            action = 'reduce'
            reasons.append(f"RSI={rsi:.1f} 超买区")
            urgency = 'medium'
        elif rsi <= 30:
            action = 'add'
            reasons.append(f"RSI={rsi:.1f} 超卖区，可加仓")
            urgency = 'medium'
        elif rsi <= 40:
            reasons.append(f"RSI={rsi:.1f} 偏低")
    
    # 趋势判断
    if trend == 'Bearish':
        if action != 'sell':
            action = 'reduce' if action not in ['sell'] else action
        reasons.append(f"趋势偏空 ({trend})")
        urgency = 'medium' if urgency == 'low' else urgency
    elif trend == 'Bullish':
        if action == 'hold':
            action = 'hold'
        reasons.append(f"趋势偏多 ({trend})")
    elif trend == 'Recovering':
        reasons.append(f"趋势转暖 ({trend})")
    elif trend == 'Weakening':
        reasons.append(f"趋势转弱 ({trend})")
    
    # MACD金叉死叉
    if macd and macd_signal:
        if macd > macd_signal and macd > 0:
            reasons.append("MACD多头排列")
        elif macd < macd_signal and macd < 0:
            reasons.append("MACD空头排列")
            if action == 'hold':
                action = 'reduce'
    
    # 近期涨幅过大
    if change_5d > 10:
        reasons.append(f"5日涨幅{change_5d:.1f}%，短期过热")
        if action == 'hold':
            action = 'reduce'
    elif change_5d < -10:
        reasons.append(f"5日跌幅{abs(change_5d):.1f}%，短期超跌")
    
    # 持仓盈利超过20%考虑止盈
    if profit_pct > 50:
        reasons.append(f"持仓盈利{profit_pct:.1f}%，建议部分止盈")
        action = 'reduce' if action == 'hold' else action
        urgency = 'medium'
    elif profit_pct > 20:
        reasons.append(f"持仓盈利{profit_pct:.1f}%")
    
    # 确定操作数量
    delta_shares = 0
    if action == 'sell':
        target_shares = 0
        delta_shares = -shares
    elif action == 'reduce':
        # 减持30-50%
        reduce_ratio = 0.3 if urgency == 'low' else 0.5
        delta_shares = -int(shares * reduce_ratio)
        target_shares = shares + delta_shares
    elif action == 'add':
        # 加仓建议 (基于当前仓位翻倍上限)
        add_ratio = 0.5
        delta_shares = int(shares * add_ratio)
        target_shares = shares + delta_shares
    
    action_cn = {
        'sell': '清仓',
        'reduce': '减持',
        'hold': '持有',
        'add': '加仓',
        'buy': '建仓'
    }.get(action, '持有')
    
    return {
        'ticker': ticker,
        'name': name,
        'price': price,
        'rsi': rsi,
        'trend': trend,
        'change_5d': change_5d,
        'change_20d': change_20d,
        'profit_pct': profit_pct,
        'shares': shares,
        'weight': weight,
        'action': action,
        'action_cn': action_cn,
        'target_shares': target_shares,
        'delta_shares': delta_shares,
        'reasons': reasons,
        'urgency': urgency
    }

# 生成所有持仓的建议
all_recommendations = []
for analysis in holdings_analysis:
    rec = generate_recommendation(analysis)
    all_recommendations.append(rec)
    
    # 分类
    if rec['action'] == 'sell':
        recommendations['sell'].append(rec)
    elif rec['action'] == 'reduce':
        recommendations['reduce'].append(rec)
    elif rec['action'] == 'add':
        recommendations['add'].append(rec)
    else:
        recommendations['hold'].append(rec)

# ============================================
# 输出分析结果
# ============================================
print("=" * 60)
print("持仓调整建议汇总")
print("=" * 60)
print()

# 卖出建议
if recommendations['sell']:
    print("🔴 【清仓建议】")
    for rec in recommendations['sell']:
        print(f"  {rec['name']} ({rec['ticker']})")
        print(f"    当前: {rec['shares']}股 @ ¥{rec['price']:.4f}")
        print(f"    建议: 清仓 {abs(rec['delta_shares'])}股")
        print(f"    原因: {', '.join(rec['reasons'])}")
    print()

# 减持建议
if recommendations['reduce']:
    print("🟠 【减持建议】")
    for rec in recommendations['reduce']:
        print(f"  {rec['name']} ({rec['ticker']})")
        print(f"    当前: {rec['shares']}股 @ ¥{rec['price']:.4f}")
        print(f"    建议: 减持 {abs(rec['delta_shares'])}股 → 目标{rec['target_shares']}股")
        print(f"    原因: {', '.join(rec['reasons'])}")
    print()

# 持有建议
if recommendations['hold']:
    print("🟢 【持有建议】")
    for rec in recommendations['hold']:
        reasons_str = ', '.join(rec['reasons']) if rec['reasons'] else '技术面中性'
        print(f"  {rec['name']} ({rec['ticker']}): {reasons_str}")
    print()

# 加仓建议
if recommendations['add']:
    print("🔵 【加仓建议】")
    for rec in recommendations['add']:
        print(f"  {rec['name']} ({rec['ticker']})")
        print(f"    当前: {rec['shares']}股 @ ¥{rec['price']:.4f}")
        print(f"    建议: 加仓 {rec['delta_shares']}股 → 目标{rec['target_shares']}股")
        print(f"    原因: {', '.join(rec['reasons'])}")
    print()

# ============================================
# 保存结果
# ============================================
output_data = {
    'analysis_time': datetime.now().isoformat(),
    'portfolio_summary': {
        'total_market_value': total_market_value,
        'estimated_total_assets': estimated_total_assets,
        'estimated_cash': estimated_cash,
        'utilization_rate': total_weight
    },
    'holdings_analysis': holdings_analysis,
    'recommendations': {
        'sell': recommendations['sell'],
        'reduce': recommendations['reduce'],
        'hold': recommendations['hold'],
        'add': recommendations['add'],
    }
}

output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)

print(f">>> 分析数据已保存至: {output_file}")
print()
print("=== 分析完成 ===")

#!/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
# -*- coding: utf-8 -*-
"""
Portfolio Adjustment Analysis - 2026-02-03
持仓调整分析 - 全量覆盖所有关注标的
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 路径设置
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_ema, calculate_atr, calculate_stochastic
)
from scripts.utils import make_serializable

# 当前持仓（从截图获取）
CURRENT_HOLDINGS = {
    '510150': {'name': '消费ETF', 'shares': 38000, 'cost': 20520.00, 'position_pct': 22.15},
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 30460.00, 'position_pct': 32.88},
    '512170': {'name': '医疗ETF', 'shares': 14000, 'cost': 4872.00, 'position_pct': 5.26},
    '512660': {'name': '军工ETF', 'shares': 8000, 'cost': 11360.00, 'position_pct': 12.26},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2328.00, 'position_pct': 2.51},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 823.20, 'position_pct': 0.89},
    '515790': {'name': '光伏ETF', 'shares': 1000, 'cost': 1058.00, 'position_pct': 1.14},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 1528.00, 'position_pct': 1.65},
    '159241': {'name': '航空TH', 'shares': 8000, 'cost': 11480.00, 'position_pct': 12.39},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 215.80, 'position_pct': 0.23},
}

# ETF候选池（从ETFs.csv）
ALL_ETFS = {
    '510150': '消费ETF', '159985': '豆粕ETF', '512890': '红利低波ETF',
    '512660': '军工ETF', '159241': '航空航天ETF天弘', '159206': '卫星ETF',
    '515790': '光伏ETF', '516780': '稀土ETF', '512170': '医疗ETF',
    '561330': '矿业ETF', '159870': '化工ETF', '561560': '电力ETF',
    '159830': '上海金ETF', '159770': '机器人ETF', '515070': '人工智能AIETF',
    '159326': '电网设备ETF', '159516': '半导体设备ETF', '515050': '通信ETF华夏',
    '161226': '国投白银LOF', '518880': '黄金ETF', '512400': '有色金属ETF',
    '510880': '红利ETF', '513180': '恒生科技指数ETF', '513630': '港股红利指数ETF',
    '588000': '科创50ETF'
}

def analyze_etf(ticker, name, is_holding=False, holding_info=None):
    """
    对单个ETF进行全面技术分析
    """
    print(f"\n{'='*60}")
    print(f"分析标的: {name} ({ticker}) {'[持仓]' if is_holding else '[候选]'}")
    print(f"{'='*60}")
    
    try:
        # 获取历史数据 (6个月)
        ticker_ts = f"{ticker}.SH" if ticker[0] in ['5', '6'] else f"{ticker}.SZ"
        data = fetch_stock_data(ticker_ts, period='6mo')
        
        if data is None or len(data) < 50:
            print(f"⚠️ 数据不足，跳过 {name}")
            return None
        
        # 计算技术指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data, window=20)
        sma20_df = calculate_sma(data, window=20)
        sma50_df = calculate_sma(data, window=50)
        ema12_df = calculate_ema(data, window=12)
        atr_df = calculate_atr(data, window=14)
        stoch_df = calculate_stochastic(data)
        
        # 当前值
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        price_change_pct = ((current_price - prev_price) / prev_price) * 100
        
        rsi = rsi_df['RSI'].iloc[-1]
        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        macd_hist = macd_df['Histogram'].iloc[-1]
        
        bb_upper = bb_df['Upper'].iloc[-1]
        bb_middle = bb_df['Middle'].iloc[-1]
        bb_lower = bb_df['Lower'].iloc[-1]
        bb_percent = ((current_price - bb_lower) / (bb_upper - bb_lower)) * 100
        
        sma20 = sma20_df['SMA'].iloc[-1]
        sma50 = sma50_df['SMA'].iloc[-1]
        atr = atr_df['ATR'].iloc[-1]
        stoch_k = stoch_df['K'].iloc[-1]
        stoch_d = stoch_df['D'].iloc[-1]
        
        # 成交量分析
        vol_avg_20 = data['Volume'].tail(20).mean()
        vol_current = data['Volume'].iloc[-1]
        vol_ratio = vol_current / vol_avg_20 if vol_avg_20 > 0 else 1.0
        
        # 趋势判断
        trend = "上升" if sma20 > sma50 else "下降"
        momentum = "强" if current_price > sma20 and sma20 > sma50 else "弱"
        
        # MACD信号
        macd_signal = "金叉" if macd_line > signal_line and macd_hist > 0 else "死叉" if macd_line < signal_line else "中性"
        
        # 综合评分 (0-100)
        score = 50  # 基准分
        
        # RSI评分 (30-70最佳，超买超卖扣分)
        if 30 <= rsi <= 70:
            score += 10
        elif rsi < 20 or rsi > 80:
            score -= 15
        
        # MACD评分
        if macd_signal == "金叉":
            score += 15
        elif macd_signal == "死叉":
            score -= 15
            
        # 布林带评分
        if 20 <= bb_percent <= 80:
            score += 10
        elif bb_percent > 90:
            score -= 10  # 接近上轨，超买
        elif bb_percent < 10:
            score += 5   # 接近下轨，可能反弹
            
        # 趋势评分
        if trend == "上升" and momentum == "强":
            score += 15
        elif trend == "下降":
            score -= 10
            
        # 成交量评分
        if vol_ratio > 1.5:
            score += 5
        elif vol_ratio < 0.5:
            score -= 5
        
        result = {
            'ticker': ticker,
            'name': name,
            'is_holding': is_holding,
            'current_price': current_price,
            'price_change_pct': price_change_pct,
            'rsi': rsi,
            'macd_line': macd_line,
            'signal_line': signal_line,
            'macd_histogram': macd_hist,
            'macd_signal': macd_signal,
            'bb_percent': bb_percent,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'sma20': sma20,
            'sma50': sma50,
            'atr': atr,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'volume_ratio': vol_ratio,
            'trend': trend,
            'momentum': momentum,
            'technical_score': score,
        }
        
        if is_holding and holding_info:
            result.update({
                'shares': holding_info['shares'],
                'cost': holding_info['cost'],
                'position_pct': holding_info['position_pct'],
                'current_value': current_price * holding_info['shares'],
                'profit_loss': (current_price * holding_info['shares']) - holding_info['cost'],
                'profit_loss_pct': ((current_price * holding_info['shares']) - holding_info['cost']) / holding_info['cost'] * 100
            })
        
        print(f"✅ 完成分析: {name} | 技术评分: {score:.1f}/100 | RSI: {rsi:.1f} | MACD: {macd_signal}")
        return result
        
    except Exception as e:
        print(f"❌ 分析失败 {name}: {str(e)}")
        return None

def main():
    print("="*80)
    print("持仓调整分析 - Portfolio Adjustment Analysis")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    all_results = []
    
    # 1. 分析当前持仓
    print("\n📊 第一部分：当前持仓诊断")
    print("="*80)
    holdings_results = []
    for ticker, info in CURRENT_HOLDINGS.items():
        result = analyze_etf(ticker, info['name'], is_holding=True, holding_info=info)
        if result:
            holdings_results.append(result)
            all_results.append(result)
    
    # 2. 分析候选品种
    print("\n\n🔍 第二部分：候选品种扫描")
    print("="*80)
    candidates_results = []
    for ticker, name in ALL_ETFS.items():
        if ticker not in CURRENT_HOLDINGS:
            result = analyze_etf(ticker, name, is_holding=False)
            if result:
                candidates_results.append(result)
                all_results.append(result)
    
    # 保存完整数据
    output_data = {
        'analysis_time': datetime.now().isoformat(),
        'total_analyzed': len(all_results),
        'current_holdings': len(holdings_results),
        'candidates': len(candidates_results),
        'holdings_results': holdings_results,
        'candidates_results': candidates_results,
        'all_results': all_results
    }
    
    clean_data = make_serializable(output_data)
    
    with open(os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json'), 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "="*80)
    print(f"✅ 分析完成！共分析 {len(all_results)} 个标的")
    print(f"   - 持仓品种: {len(holdings_results)}")
    print(f"   - 候选品种: {len(candidates_results)}")
    print(f"📁 数据已保存至: {os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')}")
    print("="*80)
    
    # 输出前5名和后5名
    sorted_results = sorted(all_results, key=lambda x: x['technical_score'], reverse=True)
    
    print("\n🏆 技术评分 TOP 5:")
    for i, r in enumerate(sorted_results[:5], 1):
        holding_tag = "[持仓]" if r['is_holding'] else "[候选]"
        print(f"  {i}. {r['name']} ({r['ticker']}) {holding_tag} - 评分: {r['technical_score']:.1f}")
    
    print("\n⚠️ 技术评分 BOTTOM 5:")
    for i, r in enumerate(sorted_results[-5:], 1):
        holding_tag = "[持仓]" if r['is_holding'] else "[候选]"
        print(f"  {i}. {r['name']} ({r['ticker']}) {holding_tag} - 评分: {r['technical_score']:.1f}")

if __name__ == "__main__":
    main()

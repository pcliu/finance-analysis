#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
布林带突破 + 成交量分析 - 2026-01-20
区分"真突破"与"假突破"
"""

import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_bollinger_bands, calculate_rsi
from scripts.utils import make_serializable

# 重点分析的突破品种
BREAKTHROUGH_TICKERS = {
    '161226': '白银基金',
    '159326': '电网设备 ETF',
    '159770': '机器人AI',
    '159830': '上海金',
}

def analyze_volume_breakthrough(ticker, name):
    """分析布林带突破的成交量特征"""
    try:
        symbol = ticker
        if ticker.startswith('5'):
            symbol = ticker + '.SS'
        elif ticker.startswith('1'):
            symbol = ticker + '.SZ'
        
        data = fetch_stock_data(symbol, period='3mo')
        if data.empty:
            return None
        
        # 计算技术指标
        bb = calculate_bollinger_bands(data, window=20, num_std=2)
        rsi = calculate_rsi(data, window=6)
        
        # 当前数据
        current_price = float(data['Close'].iloc[-1])
        current_volume = float(data['Volume'].iloc[-1])
        upper_band = float(bb['Upper'].iloc[-1])
        percent_b = float(bb['Percent_B'].iloc[-1])
        current_rsi = float(rsi['RSI'].iloc[-1])
        
        # 成交量分析
        avg_volume_20 = float(data['Volume'].rolling(20).mean().iloc[-1])
        avg_volume_5 = float(data['Volume'].rolling(5).mean().iloc[-1])
        volume_ratio_20 = current_volume / avg_volume_20
        volume_ratio_5 = current_volume / avg_volume_5
        
        # 近5日成交量趋势
        recent_volumes = data['Volume'].iloc[-5:].tolist()
        volume_trend = "放量" if current_volume > avg_volume_5 else "缩量"
        
        # 近5日价格变化
        price_5d_ago = float(data['Close'].iloc[-5])
        price_change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        
        # 判断突破类型
        is_breakthrough = percent_b > 1.0
        is_near_upper = percent_b > 0.8
        
        if is_breakthrough:
            if volume_ratio_5 > 1.3 and price_change_5d > 5:
                breakthrough_type = "🟢 真突破 (Breakout)"
                explanation = "放量突破上轨,趋势延续,可追涨"
                action = "右侧追涨 (风险较高)"
                confidence = "中等"
            elif volume_ratio_5 < 0.8:
                breakthrough_type = "🔴 假突破 (False Breakout)"
                explanation = "缩量突破上轨,动能不足,即将回落"
                action = "立即止盈"
                confidence = "高"
            else:
                breakthrough_type = "🟠 待确认突破"
                explanation = "成交量温和,需观察后续放量确认"
                action = "谨慎观望,不追高"
                confidence = "中等"
        elif is_near_upper:
            if volume_ratio_5 > 1.5:
                breakthrough_type = "⚠️ 放量冲高"
                explanation = "大量资金涌入,可能即将突破"
                action = "观察是否有效突破"
                confidence = "低"
            else:
                breakthrough_type = "✅ 正常上涨"
                explanation = "温和上涨,未过度投机"
                action = "持有观望"
                confidence = "中等"
        else:
            breakthrough_type = "✅ 正常区间"
            explanation = "价格和成交量健康"
            action = "持有"
            confidence = "高"
        
        # 结合RSI判断
        if current_rsi > 80:
            risk_level = "极高风险"
            rsi_warning = f"RSI={current_rsi:.1f}严重超买,即使放量突破也需警惕"
        elif current_rsi > 70:
            risk_level = "高风险"
            rsi_warning = f"RSI={current_rsi:.1f}超买,追高风险大"
        else:
            risk_level = "中低风险"
            rsi_warning = "RSI健康"
        
        return {
            'ticker': ticker,
            'name': name,
            'price': current_price,
            'upper_band': upper_band,
            'percent_b': percent_b,
            'rsi_6': current_rsi,
            'current_volume': current_volume,
            'avg_volume_20': avg_volume_20,
            'avg_volume_5': avg_volume_5,
            'volume_ratio_20': volume_ratio_20,
            'volume_ratio_5': volume_ratio_5,
            'volume_trend': volume_trend,
            'price_change_5d': price_change_5d,
            'breakthrough_type': breakthrough_type,
            'explanation': explanation,
            'action': action,
            'confidence': confidence,
            'risk_level': risk_level,
            'rsi_warning': rsi_warning,
        }
    except Exception as e:
        print(f"分析 {ticker} 时出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print("="*80)
    print("开始布林带突破 + 成交量分析...")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'analysis': []
    }
    
    for ticker, name in BREAKTHROUGH_TICKERS.items():
        print(f"\n分析 {ticker} ({name})...")
        analysis = analyze_volume_breakthrough(ticker, name)
        if analysis:
            results['analysis'].append(analysis)
    
    # 保存结果
    output_file = os.path.join(SCRIPT_DIR, 'volume_bollinger_data.json')
    clean_results = make_serializable(results)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n✅ 分析完成! 结果已保存至: {output_file}")
    print("="*80)
    
    # 输出摘要
    print(f"\n📊 突破类型汇总:")
    for item in results['analysis']:
        print(f"\n{item['ticker']} - {item['name']}:")
        print(f"  突破类型: {item['breakthrough_type']}")
        print(f"  成交量: {item['volume_trend']} (5日均量比={item['volume_ratio_5']:.2f}倍)")
        print(f"  Percent_B: {item['percent_b']:.1f}%")
        print(f"  RSI(6): {item['rsi_6']:.1f}")
        print(f"  建议: {item['action']}")
        print(f"  {item['rsi_warning']}")

if __name__ == '__main__':
    main()

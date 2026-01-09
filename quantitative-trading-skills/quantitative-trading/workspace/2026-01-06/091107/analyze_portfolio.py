#!/usr/bin/env python3
"""
投资组合分析脚本 - 分析当前持仓和拟建仓ETF的技术指标
"""

import sys
import os
import json
from datetime import datetime

# Add scripts path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from scripts import fetch_stock_data, calculate_rsi, calculate_sma, calculate_macd, calculate_bollinger_bands

# 当前持仓列表 (根据用户截图)
current_holdings = {
    '510880': {'name': '红利ETF', 'shares': 1000, 'market_value': 3180.00},
    '515050': {'name': '5GETF', 'shares': 500, 'market_value': 1164.00},
    '515070': {'name': 'AI智能', 'shares': 500, 'market_value': 1002.50},
    '588000': {'name': '科创50', 'shares': 8000, 'market_value': 11832.00},
    '159516': {'name': '半导体设备', 'shares': 1000, 'market_value': 1635.00},
    '159770': {'name': '机器人AI', 'shares': 1000, 'market_value': 1074.00},
    '159830': {'name': '上海金', 'shares': 400, 'market_value': 3956.00},
    '161226': {'name': '白银基金', 'shares': 500, 'market_value': 1186.00},
}

# 拟建仓ETF
potential_etfs = {
    '159241': {'name': '航空航天ETF天弘'},
    '512400': {'name': '有色金属ETF'},
    '513630': {'name': '恒生科技指数ETF'},
}

def analyze_etf(symbol: str, name: str):
    """分析单个ETF的技术指标"""
    try:
        # 使用tushare格式的代码获取数据
        # 对于沪深交易所的ETF，需要添加后缀
        if symbol.startswith('5') or symbol.startswith('6'):
            ts_code = f"{symbol}.SH"
        else:
            ts_code = f"{symbol}.SZ"
        
        print(f"\n正在分析 {name} ({symbol})...")
        
        # 获取3个月的数据，使用 tushare 数据源
        data = fetch_stock_data(ts_code, period='3mo', provider='tushare', market='cn')
        
        if data is None or len(data) == 0:
            print(f"  ⚠️ 无法获取 {symbol} 数据")
            return None
        
        # 计算技术指标
        rsi = calculate_rsi(data, period=14)
        sma_5 = calculate_sma(data, window=5)
        sma_20 = calculate_sma(data, window=20)
        macd_result = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        
        # 获取最新数据
        latest_close = data['Close'].iloc[-1]
        latest_rsi = rsi.iloc[-1] if len(rsi) > 0 else None
        latest_sma5 = sma_5.iloc[-1] if len(sma_5) > 0 else None
        latest_sma20 = sma_20.iloc[-1] if len(sma_20) > 0 else None
        latest_macd = macd_result['MACD'].iloc[-1] if 'MACD' in macd_result else None
        latest_signal = macd_result['Signal'].iloc[-1] if 'Signal' in macd_result else None
        latest_bb_upper = bb['Upper'].iloc[-1] if 'Upper' in bb else None
        latest_bb_lower = bb['Lower'].iloc[-1] if 'Lower' in bb else None
        
        # 计算价格变动
        price_1d = ((data['Close'].iloc[-1] / data['Close'].iloc[-2]) - 1) * 100 if len(data) >= 2 else 0
        price_5d = ((data['Close'].iloc[-1] / data['Close'].iloc[-5]) - 1) * 100 if len(data) >= 5 else 0
        price_20d = ((data['Close'].iloc[-1] / data['Close'].iloc[-20]) - 1) * 100 if len(data) >= 20 else 0
        
        # 趋势判断
        trend = "震荡"
        if latest_sma5 and latest_sma20:
            if latest_sma5 > latest_sma20 and latest_macd > latest_signal:
                trend = "多头"
            elif latest_sma5 < latest_sma20 and latest_macd < latest_signal:
                trend = "空头"
        
        result = {
            'symbol': symbol,
            'name': name,
            'latest_close': round(float(latest_close), 4),
            'rsi': round(float(latest_rsi), 2) if latest_rsi else None,
            'sma_5': round(float(latest_sma5), 4) if latest_sma5 else None,
            'sma_20': round(float(latest_sma20), 4) if latest_sma20 else None,
            'macd': round(float(latest_macd), 4) if latest_macd else None,
            'signal': round(float(latest_signal), 4) if latest_signal else None,
            'bb_upper': round(float(latest_bb_upper), 4) if latest_bb_upper else None,
            'bb_lower': round(float(latest_bb_lower), 4) if latest_bb_lower else None,
            'change_1d': round(price_1d, 2),
            'change_5d': round(price_5d, 2),
            'change_20d': round(price_20d, 2),
            'trend': trend
        }
        
        print(f"  ✓ {name}: 价格={latest_close:.4f}, RSI={latest_rsi:.2f}, 趋势={trend}")
        return result
        
    except Exception as e:
        print(f"  ❌ 分析 {symbol} 出错: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    output_dir = os.path.dirname(__file__)
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("投资组合分析报告")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {
        'analysis_time': datetime.now().isoformat(),
        'current_holdings': {},
        'potential_etfs': {}
    }
    
    # 分析当前持仓
    print("\n【一、当前持仓分析】")
    for symbol, info in current_holdings.items():
        analysis = analyze_etf(symbol, info['name'])
        if analysis:
            analysis['current_shares'] = info['shares']
            analysis['current_value'] = info['market_value']
            results['current_holdings'][symbol] = analysis
    
    # 分析拟建仓ETF
    print("\n【二、拟建仓ETF分析】")
    for symbol, info in potential_etfs.items():
        analysis = analyze_etf(symbol, info['name'])
        if analysis:
            results['potential_etfs'][symbol] = analysis
    
    # 保存结果
    output_file = os.path.join(output_dir, 'analysis_result.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存至: {output_file}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("分析结果摘要")
    print("=" * 60)
    
    print("\n【当前持仓】")
    print(f"{'代码':>10} {'名称':>12} {'现价':>10} {'RSI':>8} {'趋势':>6}")
    print("-" * 50)
    for symbol, data in results['current_holdings'].items():
        rsi_val = data['rsi'] if data['rsi'] else 0
        print(f"{symbol:>10} {data['name']:>12} {data['latest_close']:>10.4f} {rsi_val:>8.2f} {data['trend']:>6}")
    
    print("\n【拟建仓ETF】")
    print(f"{'代码':>10} {'名称':>20} {'现价':>10} {'RSI':>8} {'趋势':>6}")
    print("-" * 60)
    for symbol, data in results['potential_etfs'].items():
        rsi_val = data['rsi'] if data['rsi'] else 0
        print(f"{symbol:>10} {data['name']:>20} {data['latest_close']:>10.4f} {rsi_val:>8.2f} {data['trend']:>6}")

if __name__ == '__main__':
    main()

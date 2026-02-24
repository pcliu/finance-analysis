#!/usr/bin/env python3
"""
持仓调整 - 技术分析脚本
日期: 2026-02-24 (盘前分析)
覆盖: 10 持仓品种 + 15 观察品种 = 25 标的
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# === 全部标的列表 ===
ALL_ETFS = {
    # 当前持仓
    '510150': {'name': '消费ETF', 'held': True, 'shares': 38000, 'cost': 0.5559},
    '510880': {'name': '红利ETF', 'held': True, 'shares': 10000, 'cost': 3.0671},
    '512170': {'name': '医疗ETF', 'held': True, 'shares': 14000, 'cost': 0.3585},
    '512660': {'name': '军工ETF', 'held': True, 'shares': 8000, 'cost': 1.5128},
    '515050': {'name': '5GETF', 'held': True, 'shares': 1000, 'cost': 2.3200},
    '515070': {'name': 'AI智能', 'held': True, 'shares': 400, 'cost': 1.9388},
    '515790': {'name': '光伏ETF', 'held': True, 'shares': 1000, 'cost': 1.1005},
    '588000': {'name': '科创50', 'held': True, 'shares': 1000, 'cost': 0.3019},
    '159241': {'name': '航空TH', 'held': True, 'shares': 8000, 'cost': 1.5185},
    # 注意: 截图中没有机器人AI(159770)了，但之前报告里有200股
    # 从截图看确实没有159770，可能已卖出。但截图第二页显示没有159770
    # 观察品种 (ETFs.csv 中非持仓)
    '159985': {'name': '豆粕ETF', 'held': False},
    '512890': {'name': '红利低波ETF', 'held': False},
    '159206': {'name': '卫星ETF', 'held': False},
    '516780': {'name': '稀土ETF', 'held': False},
    '561330': {'name': '矿业ETF', 'held': False},
    '159870': {'name': '化工ETF', 'held': False},
    '561560': {'name': '电力ETF', 'held': False},
    '159830': {'name': '上海金ETF', 'held': False},
    '159770': {'name': '机器人ETF', 'held': False},
    '159326': {'name': '电网设备ETF', 'held': False},
    '159516': {'name': '半导体设备ETF', 'held': False},
    '161226': {'name': '国投白银LOF', 'held': False},
    '518880': {'name': '黄金ETF', 'held': False},
    '512400': {'name': '有色金属ETF', 'held': False},
    '513180': {'name': '恒生科技ETF', 'held': False},
    '513630': {'name': '港股红利ETF', 'held': False},
}

def analyze_single(code, info):
    """分析单只 ETF"""
    try:
        # 获取 6 个月日线
        data = fetch_stock_data(code, period='6mo')
        if data is None or len(data) < 30:
            return {'code': code, 'name': info['name'], 'error': 'Insufficient data'}
        
        # 计算技术指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        
        # 最新值
        close = data['Close'].iloc[-1]
        prev_close = data['Close'].iloc[-2]
        daily_change = (close - prev_close) / prev_close * 100
        
        rsi = rsi_df['RSI'].iloc[-1]
        
        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        histogram = macd_df['Histogram'].iloc[-1]
        
        # MACD 前一日
        prev_macd = macd_df['MACD'].iloc[-2]
        prev_signal = macd_df['Signal'].iloc[-2]
        
        # 判断金叉/死叉
        if macd_line > signal_line and prev_macd <= prev_signal:
            macd_status = '金叉(新)'
        elif macd_line > signal_line:
            macd_status = '金叉延续'
        elif macd_line < signal_line and prev_macd >= prev_signal:
            macd_status = '死叉(新)'
        else:
            macd_status = '死叉延续'
        
        # 布林带 %B
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        middle = bb_df['Middle'].iloc[-1]
        pct_b = (close - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
        
        # 成交量 / 20日均量
        if 'Volume' in data.columns and data['Volume'].iloc[-1] > 0:
            vol_20 = data['Volume'].iloc[-20:].mean()
            vol_ratio = data['Volume'].iloc[-1] / vol_20 if vol_20 > 0 else 1.0
        else:
            vol_ratio = 1.0
        
        # 5日涨跌幅
        if len(data) >= 6:
            five_day_change = (close - data['Close'].iloc[-6]) / data['Close'].iloc[-6] * 100
        else:
            five_day_change = 0
        
        # 20日涨跌幅
        if len(data) >= 21:
            twenty_day_change = (close - data['Close'].iloc[-21]) / data['Close'].iloc[-21] * 100
        else:
            twenty_day_change = 0
        
        result = {
            'code': code,
            'name': info['name'],
            'held': info.get('held', False),
            'shares': info.get('shares', 0),
            'cost': info.get('cost', 0),
            'close': close,
            'daily_change_pct': round(daily_change, 2),
            'five_day_change_pct': round(five_day_change, 2),
            'twenty_day_change_pct': round(twenty_day_change, 2),
            'rsi': round(rsi, 1),
            'macd': round(macd_line, 4),
            'signal': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'macd_status': macd_status,
            'bb_upper': round(upper, 4),
            'bb_middle': round(middle, 4),
            'bb_lower': round(lower, 4),
            'pct_b': round(pct_b, 2),
            'vol_ratio': round(vol_ratio, 2),
        }
        
        # 持仓盈亏计算
        if info.get('held', False) and info.get('cost', 0) > 0:
            pnl = (close - info['cost']) * info['shares']
            pnl_pct = (close - info['cost']) / info['cost'] * 100
            result['pnl'] = round(pnl, 2)
            result['pnl_pct'] = round(pnl_pct, 2)
        
        return result
    except Exception as e:
        return {'code': code, 'name': info['name'], 'error': str(e)}

def main():
    results = {}
    errors = []
    
    print(f"开始分析 {len(ALL_ETFS)} 个标的...")
    
    for code, info in ALL_ETFS.items():
        print(f"  分析 {code} ({info['name']})...")
        result = analyze_single(code, info)
        if 'error' in result:
            errors.append(result)
            print(f"    ⚠️ 错误: {result['error']}")
        else:
            results[code] = result
            print(f"    ✅ RSI={result['rsi']}, MACD={result['macd_status']}, %B={result['pct_b']}, 日涨跌={result['daily_change_pct']}%")
    
    # 分类汇总
    held_results = {k: v for k, v in results.items() if v.get('held', False)}
    watch_results = {k: v for k, v in results.items() if not v.get('held', False)}
    
    golden_cross = {k: v for k, v in results.items() if '金叉' in v.get('macd_status', '')}
    oversold = {k: v for k, v in results.items() if v.get('rsi', 50) < 40}
    overbought = {k: v for k, v in results.items() if v.get('rsi', 50) > 70}
    
    summary = {
        'analysis_date': '2026-02-24',
        'data_cutoff': '2026-02-21 (上周五收盘)',
        'total_etfs': len(results),
        'held_count': len(held_results),
        'watch_count': len(watch_results),
        'golden_cross_count': len(golden_cross),
        'golden_cross_names': [v['name'] for v in golden_cross.values()],
        'oversold_count': len(oversold),
        'oversold_names': [v['name'] for v in oversold.values()],
        'overbought_count': len(overbought),
        'overbought_names': [v['name'] for v in overbought.values()],
        'errors': errors,
    }
    
    output = {
        'summary': summary,
        'held': held_results,
        'watchlist': watch_results,
        'all': results,
    }
    
    # 保存数据
    clean_output = make_serializable(output)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 分析完成，数据已保存到: {output_path}")
    print(f"\n=== 摘要 ===")
    print(f"  成功分析: {len(results)}/{len(ALL_ETFS)}")
    print(f"  MACD金叉: {len(golden_cross)} 只 - {summary['golden_cross_names']}")
    print(f"  超卖(RSI<40): {len(oversold)} 只 - {summary['oversold_names']}")
    print(f"  超买(RSI>70): {len(overbought)} 只 - {summary['overbought_names']}")
    if errors:
        print(f"  ⚠️ 错误: {len(errors)} 只")
        for e in errors:
            print(f"    - {e['code']} ({e['name']}): {e['error']}")

if __name__ == '__main__':
    main()

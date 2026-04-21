#!/usr/bin/env python3
"""
持仓调整技术分析脚本 - 2026-02-10
分析所有持仓标的和ETFs.csv中的观察标的
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma, calculate_atr
from scripts.utils import make_serializable

# ============ 当前持仓 (从截图提取 2026-02-10) ============
holdings = {
    '510150': {'name': '消费ETF', 'shares': 38000, 'cost': 0.5559, 'price': 0.5600, 'pnl': 155.44, 'pnl_pct': 0.74, 'position_pct': 22.29},
    '510880': {'name': '红利ETF', 'shares': 10000, 'cost': 3.0671, 'price': 3.1440, 'pnl': 767.43, 'pnl_pct': 2.51, 'position_pct': 32.93},
    '512170': {'name': '医疗ETF', 'shares': 14000, 'cost': 0.3585, 'price': 0.3590, 'pnl': 6.50, 'pnl_pct': 0.14, 'position_pct': 5.26},
    '512660': {'name': '军工ETF', 'shares': 8000, 'cost': 1.5128, 'price': 1.4660, 'pnl': -374.59, 'pnl_pct': -3.09, 'position_pct': 12.28},
    '515050': {'name': '5GETF', 'shares': 1000, 'cost': 2.3200, 'price': 2.3480, 'pnl': 27.50, 'pnl_pct': 1.21, 'position_pct': 2.46},
    '515070': {'name': 'AI智能', 'shares': 400, 'cost': 1.9388, 'price': 2.0150, 'pnl': 30.00, 'pnl_pct': 3.93, 'position_pct': 0.84},
    '515790': {'name': '光伏ETF', 'shares': 1000, 'cost': 1.1005, 'price': 1.1440, 'pnl': 43.00, 'pnl_pct': 3.95, 'position_pct': 1.20},
    '588000': {'name': '科创50', 'shares': 1000, 'cost': 0.3019, 'price': 1.5350, 'pnl': 1232.60, 'pnl_pct': 408.45, 'position_pct': 1.61},
    '159241': {'name': '航天TH', 'shares': 8000, 'cost': 1.5185, 'price': 1.4940, 'pnl': -196.60, 'pnl_pct': -1.61, 'position_pct': 12.52},
    '159770': {'name': '机器人AI', 'shares': 200, 'cost': 0.7670, 'price': 1.1070, 'pnl': 67.50, 'pnl_pct': 44.33, 'position_pct': 0.23},
}

# ============ ETFs.csv 全部品种 (包含持仓和非持仓) ============
all_etfs = {
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

# ============ 账户总览 ============
account = {
    'total_assets': 95476.21,
    'market_value': 87480.40,
    'available_cash': 7995.81,
    'total_pnl': 1822.36,
    'today_pnl': 849.00,
}

def analyze_single_etf(code, name, period='8mo'):
    """分析单个ETF的技术指标"""
    try:
        print(f"  正在获取 {code} ({name}) 数据...")
        data = fetch_stock_data(code, period=period)
        if data is None or data.empty:
            print(f"  ⚠️  {code} ({name}) 数据为空，跳过")
            return None

        # 计算指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        sma20 = calculate_sma(data, window=20)
        sma60 = calculate_sma(data, window=60)

        # 最新价格
        latest_close = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2]) if len(data) > 1 else latest_close
        daily_change = (latest_close - prev_close) / prev_close * 100

        # 5日涨跌
        if len(data) >= 6:
            five_day_ago = float(data['Close'].iloc[-6])
            five_day_change = (latest_close - five_day_ago) / five_day_ago * 100
        else:
            five_day_change = 0

        # 20日涨跌
        if len(data) >= 21:
            twenty_day_ago = float(data['Close'].iloc[-21])
            twenty_day_change = (latest_close - twenty_day_ago) / twenty_day_ago * 100
        else:
            twenty_day_change = 0

        # RSI
        current_rsi = float(rsi_df['RSI'].iloc[-1]) if not rsi_df['RSI'].isna().iloc[-1] else None
        prev_rsi = float(rsi_df['RSI'].iloc[-2]) if len(rsi_df) > 1 and not rsi_df['RSI'].isna().iloc[-2] else None

        # MACD
        macd_line = float(macd_df['MACD'].iloc[-1]) if not macd_df['MACD'].isna().iloc[-1] else None
        signal_line = float(macd_df['Signal'].iloc[-1]) if not macd_df['Signal'].isna().iloc[-1] else None
        histogram = float(macd_df['Histogram'].iloc[-1]) if not macd_df['Histogram'].isna().iloc[-1] else None
        prev_histogram = float(macd_df['Histogram'].iloc[-2]) if len(macd_df) > 1 and not macd_df['Histogram'].isna().iloc[-2] else None
        macd_cross = 'golden' if (macd_line and signal_line and macd_line > signal_line) else 'death'

        # Bollinger Bands %B
        if 'Percent_B' in bb_df.columns:
            percent_b = float(bb_df['Percent_B'].iloc[-1]) if not bb_df['Percent_B'].isna().iloc[-1] else None
        elif '%B' in bb_df.columns:
            percent_b = float(bb_df['%B'].iloc[-1]) if not bb_df['%B'].isna().iloc[-1] else None
        else:
            # Calculate manually
            upper = float(bb_df['Upper'].iloc[-1])
            lower = float(bb_df['Lower'].iloc[-1])
            if upper != lower:
                percent_b = (latest_close - lower) / (upper - lower)
            else:
                percent_b = 0.5

        bb_upper = float(bb_df['Upper'].iloc[-1]) if not bb_df['Upper'].isna().iloc[-1] else None
        bb_lower = float(bb_df['Lower'].iloc[-1]) if not bb_df['Lower'].isna().iloc[-1] else None
        bb_middle = float(bb_df['Middle'].iloc[-1]) if not bb_df['Middle'].isna().iloc[-1] else None

        # SMA
        sma20_val = float(sma20['SMA'].iloc[-1]) if not sma20['SMA'].isna().iloc[-1] else None
        sma60_val = float(sma60['SMA'].iloc[-1]) if not sma60['SMA'].isna().iloc[-1] else None

        # 成交量分析
        vol_current = float(data['Volume'].iloc[-1])
        vol_20avg = float(data['Volume'].iloc[-20:].mean()) if len(data) >= 20 else float(data['Volume'].mean())
        vol_ratio = vol_current / vol_20avg if vol_20avg > 0 else 1.0

        # 5日RSI趋势
        rsi_5d = []
        for i in range(-5, 0):
            if len(rsi_df) > abs(i) and not rsi_df['RSI'].isna().iloc[i]:
                rsi_5d.append(float(rsi_df['RSI'].iloc[i]))

        result = {
            'code': code,
            'name': name,
            'latest_close': latest_close,
            'prev_close': prev_close,
            'daily_change_pct': round(daily_change, 2),
            'five_day_change_pct': round(five_day_change, 2),
            'twenty_day_change_pct': round(twenty_day_change, 2),
            'rsi': round(current_rsi, 2) if current_rsi else None,
            'prev_rsi': round(prev_rsi, 2) if prev_rsi else None,
            'macd_line': round(macd_line, 6) if macd_line else None,
            'signal_line': round(signal_line, 6) if signal_line else None,
            'histogram': round(histogram, 6) if histogram else None,
            'prev_histogram': round(prev_histogram, 6) if prev_histogram else None,
            'macd_cross': macd_cross,
            'percent_b': round(percent_b, 4) if percent_b is not None else None,
            'bb_upper': round(bb_upper, 4) if bb_upper else None,
            'bb_lower': round(bb_lower, 4) if bb_lower else None,
            'bb_middle': round(bb_middle, 4) if bb_middle else None,
            'sma20': round(sma20_val, 4) if sma20_val else None,
            'sma60': round(sma60_val, 4) if sma60_val else None,
            'volume': vol_current,
            'vol_20avg': round(vol_20avg, 0),
            'vol_ratio': round(vol_ratio, 2),
            'rsi_5d_trend': rsi_5d,
            'is_holding': code in holdings,
        }

        if code in holdings:
            result['holding_info'] = holdings[code]

        print(f"  ✅ {code} ({name}): 收盘={latest_close:.4f}, RSI={current_rsi:.1f}, %B={percent_b:.3f}, MACD={macd_cross}")
        return result

    except Exception as e:
        print(f"  ❌ {code} ({name}) 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    print("=" * 60)
    print("持仓调整技术分析 - 2026-02-10")
    print("=" * 60)
    
    results = {}
    
    # 分析所有ETF
    print(f"\n📊 分析 {len(all_etfs)} 个标的...")
    for code, name in all_etfs.items():
        result = analyze_single_etf(code, name)
        if result:
            results[code] = result
    
    # 汇总
    output = {
        'analysis_date': '2026-02-10',
        'account': account,
        'holdings': holdings,
        'technical_data': results,
        'summary': {
            'total_analyzed': len(results),
            'total_holdings': len(holdings),
            'total_watchlist': len(all_etfs) - len(holdings),
        }
    }
    
    # 保存JSON
    clean_output = make_serializable(output)
    output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 数据已保存至: {output_path}")
    
    # 打印摘要表
    print("\n" + "=" * 100)
    print(f"{'代码':<10} {'名称':<15} {'收盘价':<10} {'日涨跌%':<10} {'RSI':<8} {'%B':<8} {'MACD':<8} {'量比':<8} {'持仓':<6}")
    print("-" * 100)
    
    # 按RSI排序
    sorted_results = sorted(results.values(), key=lambda x: x.get('rsi', 0) if x.get('rsi') else 0, reverse=True)
    for r in sorted_results:
        hold_mark = "★" if r['is_holding'] else ""
        print(f"{r['code']:<10} {r['name']:<15} {r['latest_close']:<10.4f} {r['daily_change_pct']:>+8.2f}% {r.get('rsi', 'N/A'):<8} {r.get('percent_b', 'N/A'):<8} {r['macd_cross']:<8} {r['vol_ratio']:<8.2f} {hold_mark}")
    
    print("=" * 100)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
持仓调整技术分析脚本 - 2026-02-28
对所有持仓 + ETFs.csv 中的品种进行全量技术面诊断
"""
import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands
from scripts.utils import make_serializable

# ============================
# 全部标的列表 (持仓 + ETFs.csv)
# ============================
ALL_ETFS = {
    # 当前持仓 (11只)
    '510150': '消费ETF',
    '510880': '红利ETF',
    '512170': '医疗ETF',
    '512660': '军工ETF',
    '513180': '恒生科技ETF',
    '515050': '5GETF',
    '515070': 'AI智能',
    '515790': '光伏ETF',
    '588000': '科创50',
    '159241': '航空TH',
    '159770': '机器人AI',
    # ETFs.csv 中未持仓品种 (14只)
    '159985': '豆粕ETF',
    '512890': '红利低波ETF',
    '159206': '卫星ETF',
    '516780': '稀土ETF',
    '561330': '矿业ETF',
    '159870': '化工ETF',
    '561560': '电力ETF',
    '159830': '上海金ETF',
    '159326': '电网设备ETF',
    '159516': '半导体设备ETF',
    '161226': '国投白银LOF',
    '518880': '黄金ETF',
    '512400': '有色金属ETF',
    '513630': '港股红利ETF',
}

HELD_CODES = ['510150', '510880', '512170', '512660', '513180', '515050',
              '515070', '515790', '588000', '159241', '159770']

# 持仓详情 (2/27 收盘后截图数据)
HOLDINGS = {
    '510150': {'shares': 38000, 'cost': 0.5559, 'current': 0.5440, 'market_value': 20672, 'pnl': -452.53, 'pnl_pct': -2.14, 'position_pct': 21.37, 'day_pnl': 0.00, 'day_pnl_pct': 0.00},
    '510880': {'shares': 10000, 'cost': 3.0671, 'current': 3.2320, 'market_value': 32320, 'pnl': 1647.38, 'pnl_pct': 5.38, 'position_pct': 33.41, 'day_pnl': 370, 'day_pnl_pct': 1.16},
    '512170': {'shares': 14000, 'cost': 0.3585, 'current': 0.3540, 'market_value': 4956, 'pnl': -63.50, 'pnl_pct': -1.26, 'position_pct': 5.12, 'day_pnl': 28, 'day_pnl_pct': 0.57},
    '512660': {'shares': 8000, 'cost': 1.5128, 'current': 1.5500, 'market_value': 12400, 'pnl': 297.38, 'pnl_pct': 2.46, 'position_pct': 12.82, 'day_pnl': -16, 'day_pnl_pct': -0.13},
    '513180': {'shares': 5000, 'cost': 0.7001, 'current': 0.6700, 'market_value': 3350, 'pnl': -151.00, 'pnl_pct': -4.30, 'position_pct': 3.46, 'day_pnl': 15, 'day_pnl_pct': 0.45},
    '515050': {'shares': 1000, 'cost': 2.3200, 'current': 2.4240, 'market_value': 2424, 'pnl': 103.50, 'pnl_pct': 4.48, 'position_pct': 2.51, 'day_pnl': -39, 'day_pnl_pct': -1.58},
    '515070': {'shares': 400, 'cost': 1.9388, 'current': 2.0470, 'market_value': 818.80, 'pnl': 42.80, 'pnl_pct': 5.58, 'position_pct': 0.85, 'day_pnl': -2.40, 'day_pnl_pct': -0.29},
    '515790': {'shares': 1000, 'cost': 1.1005, 'current': 1.1360, 'market_value': 1136, 'pnl': 35.00, 'pnl_pct': 3.23, 'position_pct': 1.17, 'day_pnl': 18, 'day_pnl_pct': 1.61},
    '588000': {'shares': 1000, 'cost': 0.3019, 'current': 1.5660, 'market_value': 1566, 'pnl': 1263.60, 'pnl_pct': 418.71, 'position_pct': 1.62, 'day_pnl': 2, 'day_pnl_pct': 0.13},
    '159241': {'shares': 8000, 'cost': 1.5185, 'current': 1.5460, 'market_value': 12368, 'pnl': 219.38, 'pnl_pct': 1.81, 'position_pct': 12.79, 'day_pnl': -40, 'day_pnl_pct': -0.32},
    '159770': {'shares': 200, 'cost': 0.7670, 'current': 1.1230, 'market_value': 224.60, 'pnl': 70.70, 'pnl_pct': 46.41, 'position_pct': 0.23, 'day_pnl': 0.40, 'day_pnl_pct': 0.18},
}

AVAILABLE_CASH = 497.75  # 可用资金

def analyze_single(code, name):
    """对单个ETF进行完整的技术面分析"""
    try:
        data = fetch_stock_data(code, period='6mo')
        if data is None or len(data) < 30:
            return {'code': code, 'name': name, 'error': 'Data fetch failed or insufficient data'}
        
        # 计算指标
        rsi_df = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb_df = calculate_bollinger_bands(data)
        
        # 获取最新值
        close = data['Close'].iloc[-1]
        close_prev = data['Close'].iloc[-2] if len(data) > 1 else close
        
        rsi = rsi_df['RSI'].iloc[-1]
        rsi_prev = rsi_df['RSI'].iloc[-2] if len(rsi_df) > 1 else rsi
        
        macd_line = macd_df['MACD'].iloc[-1]
        signal_line = macd_df['Signal'].iloc[-1]
        histogram = macd_df['Histogram'].iloc[-1]
        macd_prev = macd_df['MACD'].iloc[-2] if len(macd_df) > 1 else macd_line
        signal_prev = macd_df['Signal'].iloc[-2] if len(macd_df) > 1 else signal_line
        hist_prev = macd_df['Histogram'].iloc[-2] if len(macd_df) > 1 else histogram
        
        upper = bb_df['Upper'].iloc[-1]
        lower = bb_df['Lower'].iloc[-1]
        middle = bb_df['Middle'].iloc[-1]
        bb_width = (upper - lower) / middle if middle != 0 else 0
        pct_b = (close - lower) / (upper - lower) if (upper - lower) != 0 else 0.5
        
        # MACD金叉/死叉判断
        golden_cross_today = (macd_prev <= signal_prev) and (macd_line > signal_line)
        death_cross_today = (macd_prev >= signal_prev) and (macd_line < signal_line)
        is_golden = macd_line > signal_line
        
        if golden_cross_today:
            macd_status = '金叉(新)'
        elif death_cross_today:
            macd_status = '死叉(新)'
        elif is_golden:
            macd_status = '金叉延续'
        else:
            macd_status = '死叉延续'
        
        # 涨跌幅
        change_1d = (close / close_prev - 1) * 100 if close_prev != 0 else 0
        
        close_5d = data['Close'].iloc[-6] if len(data) > 5 else data['Close'].iloc[0]
        change_5d = (close / close_5d - 1) * 100 if close_5d != 0 else 0
        
        close_20d = data['Close'].iloc[-21] if len(data) > 20 else data['Close'].iloc[0]
        change_20d = (close / close_20d - 1) * 100 if close_20d != 0 else 0
        
        # 成交量比率
        vol_current = data['Volume'].iloc[-1]
        vol_avg_20 = data['Volume'].iloc[-21:].mean() if len(data) > 20 else data['Volume'].mean()
        vol_ratio = vol_current / vol_avg_20 if vol_avg_20 > 0 else 1.0
        
        # 5日RSI趋势
        rsi_5d_ago = rsi_df['RSI'].iloc[-6] if len(rsi_df) > 5 else rsi_df['RSI'].iloc[0]
        rsi_change_5d = rsi - rsi_5d_ago
        
        result = {
            'code': code,
            'name': name,
            'close': round(close, 4),
            'change_1d': round(change_1d, 2),
            'change_5d': round(change_5d, 2),
            'change_20d': round(change_20d, 2),
            'rsi': round(rsi, 1),
            'rsi_prev': round(rsi_prev, 1),
            'rsi_change_5d': round(rsi_change_5d, 1),
            'pct_b': round(pct_b, 2),
            'bb_width': round(bb_width, 4),
            'bb_upper': round(upper, 4),
            'bb_lower': round(lower, 4),
            'bb_middle': round(middle, 4),
            'macd': round(macd_line, 4),
            'signal': round(signal_line, 4),
            'histogram': round(histogram, 4),
            'hist_prev': round(hist_prev, 4),
            'macd_status': macd_status,
            'is_golden': is_golden,
            'golden_cross_today': golden_cross_today,
            'death_cross_today': death_cross_today,
            'vol_ratio': round(vol_ratio, 2),
            'is_held': code in HELD_CODES,
        }
        
        if code in HOLDINGS:
            h = HOLDINGS[code]
            result.update({
                'shares': h['shares'],
                'cost': h['cost'],
                'market_value': h['market_value'],
                'pnl': h['pnl'],
                'pnl_pct': h['pnl_pct'],
                'position_pct': h['position_pct'],
                'day_pnl': h['day_pnl'],
                'day_pnl_pct': h['day_pnl_pct'],
            })
        
        return result
        
    except Exception as e:
        return {'code': code, 'name': name, 'error': str(e)}

# ========== 主执行 ==========
print("=" * 60)
print("持仓调整技术分析 - 2026-02-28 盘前")
print("=" * 60)

results = {}
errors = []

for code, name in ALL_ETFS.items():
    print(f"  分析: {name} ({code})...", end=" ")
    r = analyze_single(code, name)
    if 'error' in r:
        print(f"❌ {r['error']}")
        errors.append(r)
    else:
        print(f"✅ RSI={r['rsi']} %B={r['pct_b']} MACD={r['macd_status']} 1d={r['change_1d']:+.2f}%")
        results[code] = r

# 分类输出
print("\n" + "=" * 60)
print("📊 技术指标汇总")
print("=" * 60)

# 按RSI排序
sorted_results = sorted(results.values(), key=lambda x: x['rsi'], reverse=True)

print(f"\n{'代码':<8} {'名称':<12} {'RSI':>5} {'%B':>5} {'MACD状态':<10} {'1d':>7} {'5d':>7} {'20d':>7} {'Vol比':>5} {'持仓':>4}")
print("-" * 90)
for r in sorted_results:
    held = "✅" if r['is_held'] else "—"
    print(f"{r['code']:<8} {r['name']:<12} {r['rsi']:>5.1f} {r['pct_b']:>5.2f} {r['macd_status']:<10} {r['change_1d']:>+6.2f}% {r['change_5d']:>+6.2f}% {r['change_20d']:>+6.2f}% {r['vol_ratio']:>5.2f} {held}")

# 金叉品种
print("\n🟢 金叉品种:")
golden = [r for r in sorted_results if r['is_golden']]
for r in golden:
    flag = "⭐新金叉" if r['golden_cross_today'] else "延续"
    print(f"  {r['name']}({r['code']}): RSI={r['rsi']} %B={r['pct_b']} Hist={r['histogram']:+.4f} [{flag}]")

# 死叉新形成
print("\n🔴 新死叉品种:")
new_death = [r for r in sorted_results if r.get('death_cross_today', False)]
for r in new_death:
    print(f"  {r['name']}({r['code']}): RSI={r['rsi']} %B={r['pct_b']} Hist={r['histogram']:+.4f}")
if not new_death:
    print("  (无)")

# 超买/过热
print("\n⚠️ 过热品种 (RSI>60 or %B>0.9):")
hot = [r for r in sorted_results if r['rsi'] > 60 or r['pct_b'] > 0.9]
for r in hot:
    print(f"  {r['name']}({r['code']}): RSI={r['rsi']} %B={r['pct_b']}")

# 超卖
print("\n🔽 弱势品种 (RSI<45):")
weak = [r for r in sorted_results if r['rsi'] < 45]
for r in weak:
    print(f"  {r['name']}({r['code']}): RSI={r['rsi']} %B={r['pct_b']}")

# 保存数据
all_data = {
    'date': '2026-02-28',
    'analysis_time': '08:57',
    'available_cash': AVAILABLE_CASH,
    'total_etfs': len(ALL_ETFS),
    'successful': len(results),
    'failed': len(errors),
    'holdings': HOLDINGS,
    'results': results,
    'errors': errors
}

clean_data = make_serializable(all_data)
output_path = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, indent=4, ensure_ascii=False)

print(f"\n✅ 数据已保存至: {output_path}")
print(f"成功分析: {len(results)}/{len(ALL_ETFS)} 只标的")
if errors:
    print(f"失败: {len(errors)} 只 - {[e['code'] for e in errors]}")

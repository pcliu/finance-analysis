#!/usr/bin/env python3
"""
ETF 关联度分析 - 找出高度相关的 ETF 并给出删减建议
"""
import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data
from scripts.utils import make_serializable
import pandas as pd
import numpy as np

# ETF 列表 (从 ETFs.csv 读取)
etfs = {
    '510880': '红利 ETF',
    '510150': '消费 ETF',
    '512170': '医疗 ETF',
    '159985': '豆粕 ETF',
    '159689': '粮食 ETF',
    '159930': '能源 ETF',
    '159870': '化工 ETF',
    '561330': '矿业 ETF',
    '561560': '电力 ETF',
    '159326': '电网设备 ETF',
    '515790': '光伏 ETF',
    '512660': '军工 ETF',
    '159241': '航空航天 ETF',
    '159206': '卫星 ETF',
    '159830': '上海金 ETF',
    '161226': '国投白银 LOF',
    '518880': '黄金 ETF',
    '512400': '有色金属 ETF',
    '159770': '机器人 ETF',
    '515070': '人工智能 AIETF',
    '159516': '半导体设备 ETF',
    '515050': '通信 ETF',
    '588000': '科创 50ETF',
    '513180': '恒生科技指数 ETF',
    '513630': '港股红利指数 ETF',
}

print(f"正在获取 {len(etfs)} 只 ETF 的历史数据...")
print("=" * 60)

# 获取所有 ETF 的历史收盘价数据 (使用 6 个月数据)
close_prices = {}
failed = []

for code, name in etfs.items():
    try:
        data = fetch_stock_data(code, period='6mo')
        if data is not None and len(data) > 20:
            close_prices[code] = data['Close']
            print(f"  ✅ {name} ({code}): {len(data)} 条数据")
        else:
            print(f"  ❌ {name} ({code}): 数据不足")
            failed.append(code)
    except Exception as e:
        print(f"  ❌ {name} ({code}): 获取失败 - {str(e)[:50]}")
        failed.append(code)

print(f"\n成功获取 {len(close_prices)} 只 ETF 的数据")
if failed:
    print(f"获取失败: {[etfs[c] for c in failed]}")

# 构建收盘价 DataFrame
df_close = pd.DataFrame(close_prices)
df_close = df_close.dropna(how='all')
df_close = df_close.fillna(method='ffill')  # 前向填充

# 计算日收益率
returns = df_close.pct_change().dropna()

# 计算相关性矩阵
corr_matrix = returns.corr()

# 找出高度相关的 ETF 对 (相关系数 > 0.7)
print("\n" + "=" * 60)
print("📊 高度相关的 ETF 对 (|相关系数| > 0.7)")
print("=" * 60)

high_corr_pairs = []
n = len(corr_matrix.columns)
for i in range(n):
    for j in range(i+1, n):
        code_i = corr_matrix.columns[i]
        code_j = corr_matrix.columns[j]
        corr_val = corr_matrix.iloc[i, j]
        if abs(corr_val) > 0.7:
            high_corr_pairs.append({
                'etf1_code': code_i,
                'etf1_name': etfs[code_i],
                'etf2_code': code_j,
                'etf2_name': etfs[code_j],
                'correlation': round(corr_val, 4)
            })

# 按相关系数绝对值排序
high_corr_pairs.sort(key=lambda x: abs(x['correlation']), reverse=True)

for pair in high_corr_pairs:
    emoji = "🔴" if abs(pair['correlation']) > 0.85 else "🟡"
    print(f"  {emoji} {pair['etf1_name']} ↔ {pair['etf2_name']}: {pair['correlation']:.4f}")

# 聚类分析 - 找出高度相关的 ETF 组
print("\n" + "=" * 60)
print("📋 关联度聚类分组")
print("=" * 60)

# 使用 Union-Find 进行聚类 (阈值 0.75)
CLUSTER_THRESHOLD = 0.75
parent = {code: code for code in corr_matrix.columns}

def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x

def union(x, y):
    px, py = find(x), find(y)
    if px != py:
        parent[px] = py

for i in range(n):
    for j in range(i+1, n):
        code_i = corr_matrix.columns[i]
        code_j = corr_matrix.columns[j]
        if abs(corr_matrix.iloc[i, j]) > CLUSTER_THRESHOLD:
            union(code_i, code_j)

# 收集聚类
clusters = {}
for code in corr_matrix.columns:
    root = find(code)
    if root not in clusters:
        clusters[root] = []
    clusters[root].append(code)

# 只关心包含多个 ETF 的聚类
multi_clusters = {k: v for k, v in clusters.items() if len(v) > 1}

# 计算每个 ETF 的 6 个月收益率和波动率，以辅助选择
perf_metrics = {}
for code in corr_matrix.columns:
    ret = returns[code]
    total_return = (1 + ret).prod() - 1
    volatility = ret.std() * np.sqrt(252)
    sharpe = (ret.mean() * 252) / (ret.std() * np.sqrt(252)) if ret.std() > 0 else 0
    perf_metrics[code] = {
        'total_return': round(total_return * 100, 2),
        'volatility': round(volatility * 100, 2),
        'sharpe': round(sharpe, 2),
        'avg_daily_volume': 0  # placeholder
    }

cluster_analysis = []
for idx, (root, members) in enumerate(multi_clusters.items(), 1):
    print(f"\n  🏷️ 聚类 {idx}:")
    cluster_info = {'cluster_id': idx, 'members': []}
    
    # 计算组内平均相关系数
    if len(members) > 1:
        pair_corrs = []
        for mi in range(len(members)):
            for mj in range(mi+1, len(members)):
                pair_corrs.append(corr_matrix.loc[members[mi], members[mj]])
        avg_corr = np.mean(pair_corrs)
    else:
        avg_corr = 1.0
    
    print(f"     组内平均相关系数: {avg_corr:.4f}")
    
    for code in members:
        m = perf_metrics[code]
        print(f"     - {etfs[code]} ({code}): 收益 {m['total_return']:+.2f}%, 波动 {m['volatility']:.2f}%, Sharpe {m['sharpe']:.2f}")
        cluster_info['members'].append({
            'code': code,
            'name': etfs[code],
            'total_return': m['total_return'],
            'volatility': m['volatility'],
            'sharpe': m['sharpe']
        })
    
    cluster_info['avg_correlation'] = round(avg_corr, 4)
    cluster_analysis.append(cluster_info)

# 独立 ETF (不与其他ETF高度相关)
independent = [code for code in corr_matrix.columns if find(code) == code and len(clusters.get(code, [])) == 1]
print(f"\n  🟢 独立 ETF (与其他 ETF 关联度较低):")
for code in independent:
    m = perf_metrics[code]
    print(f"     - {etfs[code]} ({code}): 收益 {m['total_return']:+.2f}%, 波动 {m['volatility']:.2f}%, Sharpe {m['sharpe']:.2f}")

# 给出删减建议
print("\n" + "=" * 60)
print("✂️ 删减建议")
print("=" * 60)

to_remove = []
to_keep = []

for cluster_info in cluster_analysis:
    members = cluster_info['members']
    if len(members) <= 1:
        continue
    
    # 按 Sharpe 比率排序，保留最优的
    members_sorted = sorted(members, key=lambda x: x['sharpe'], reverse=True)
    best = members_sorted[0]
    rest = members_sorted[1:]
    
    print(f"\n  聚类 {cluster_info['cluster_id']} (平均相关系数: {cluster_info['avg_correlation']:.4f}):")
    print(f"    ✅ 建议保留: {best['name']} ({best['code']}) - Sharpe {best['sharpe']:.2f}")
    for r in rest:
        print(f"    ❌ 建议删除: {r['name']} ({r['code']}) - Sharpe {r['sharpe']:.2f}")
        to_remove.append({'code': r['code'], 'name': r['name'], 'reason': f"与 {best['name']} 高度相关 (组内平均相关系数 {cluster_info['avg_correlation']:.4f})，且 Sharpe 较低 ({r['sharpe']:.2f} vs {best['sharpe']:.2f})"})

for code in independent:
    to_keep.append({'code': code, 'name': etfs[code]})

for cluster_info in cluster_analysis:
    members_sorted = sorted(cluster_info['members'], key=lambda x: x['sharpe'], reverse=True)
    if members_sorted:
        to_keep.append({'code': members_sorted[0]['code'], 'name': members_sorted[0]['name']})

print(f"\n📊 总结:")
print(f"  当前 ETF 数量: {len(close_prices)}")
print(f"  建议删除: {len(to_remove)} 只")
print(f"  建议保留: {len(close_prices) - len(to_remove)} 只")

print(f"\n  🗑️ 建议删除的 ETF:")
for r in to_remove:
    print(f"     - {r['name']} ({r['code']}): {r['reason']}")

print(f"\n  ✅ 建议保留的 ETF:")
remaining_codes = set(close_prices.keys()) - set(r['code'] for r in to_remove)
for code in remaining_codes:
    print(f"     - {etfs[code]} ({code})")

# 保存结果
results = {
    'high_corr_pairs': high_corr_pairs,
    'cluster_analysis': cluster_analysis,
    'independent_etfs': [{'code': c, 'name': etfs[c]} for c in independent],
    'to_remove': to_remove,
    'remaining': [{'code': c, 'name': etfs[c]} for c in remaining_codes],
    'performance_metrics': {code: perf_metrics[code] for code in close_prices},
    'correlation_matrix': {code: {c2: round(corr_matrix.loc[code, c2], 4) for c2 in corr_matrix.columns} for code in corr_matrix.columns}
}

clean_results = make_serializable(results)
output_path = os.path.join(SCRIPT_DIR, 'correlation_analysis_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_results, f, indent=4, ensure_ascii=False)

print(f"\n📁 结果已保存到: {output_path}")

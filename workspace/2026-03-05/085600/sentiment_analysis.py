#!/usr/bin/env python3
"""
舆情扫描 - 2026-03-05 盘前
关键词：消费、医疗、军工、科技、光伏、AI、半导体、稀土、黄金、航天、科创、机器人、红利、两会、港股、有色
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# AkShare
import akshare as ak
import pandas as pd

KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土',
    '黄金', '航天', '科创', '机器人', '红利', '两会', '港股', '有色金属',
    '5G', '通信', '电力', '化工', '国防', '恒生科技', '航空', '白银'
]

# Simple sentiment function
POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '飙升',
                  '回暖', '反弹', '走强', '新高', '涨停', '看好', '加码', '牛市',
                  '拉升', '暴涨', '升温', '火爆', '加速', '放量', '爆发', '景气',
                  '催化', '支撑', '底部', '企稳', '修复', '回升']
NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '大跌', '跌停',
                  '下挫', '走弱', '回调', '新低', '抛售', '恐慌', '缩量', '熊市',
                  '跳水', '暴跌', '降温', '低迷', '承压', '萎缩', '爆雷', '衰退',
                  '警告', '危机', '封锁', '制裁', '冲击', '紧张']

def simple_sentiment(text):
    if not text:
        return 'neutral'
    pos = sum(1 for w in POSITIVE_WORDS if w in str(text))
    neg = sum(1 for w in NEGATIVE_WORDS if w in str(text))
    if pos > neg:
        return 'positive'
    elif neg > pos:
        return 'negative'
    return 'neutral'

results = {}

# 1. 东方财富新闻
print("=== 东方财富新闻扫描 ===")
for kw in KEYWORDS:
    try:
        news = ak.stock_news_em(symbol=kw)
        if news is not None and not news.empty:
            news = news.head(5)
            sentiments = []
            titles = []
            for _, row in news.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                s = simple_sentiment(title + ' ' + content)
                sentiments.append(s)
                titles.append(title)
            
            pos = sentiments.count('positive')
            neg = sentiments.count('negative')
            neu = sentiments.count('neutral')
            
            if pos > neg:
                overall = 'positive'
            elif neg > pos:
                overall = 'negative'
            else:
                overall = 'neutral'
            
            results[kw] = {
                'overall': overall,
                'positive': pos,
                'negative': neg,
                'neutral': neu,
                'titles': titles[:5],
                'source': '东方财富'
            }
            emoji = '🟢' if overall == 'positive' else ('🔴' if overall == 'negative' else '🟡')
            print(f"  {emoji} {kw}: {overall} ({pos}/{neg}/{neu}) | {titles[0][:40]}")
        else:
            results[kw] = {'overall': 'neutral', 'positive': 0, 'negative': 0, 'neutral': 0, 'titles': [], 'source': 'no_data'}
            print(f"  ⚪ {kw}: 无数据")
    except Exception as e:
        results[kw] = {'overall': 'neutral', 'error': str(e)[:100]}
        print(f"  ❌ {kw}: {str(e)[:60]}")

# 2. 百度经济新闻
print("\n=== 百度经济新闻 ===")
try:
    econ_news = ak.news_economic_baidu()
    if econ_news is not None and not econ_news.empty:
        econ_titles = []
        for _, row in econ_news.head(10).iterrows():
            title = str(row.get('title', row.get('标题', '')))
            econ_titles.append(title)
            print(f"  📰 {title[:60]}")
        results['_baidu_economic'] = {'titles': econ_titles}
except Exception as e:
    print(f"  ❌ 百度经济新闻: {e}")
    results['_baidu_economic'] = {'error': str(e)[:100]}

# 3. CCTV新闻
print("\n=== CCTV新闻 ===")
try:
    cctv = ak.news_cctv(date="20260304")
    if cctv is not None and not cctv.empty:
        cctv_titles = []
        for _, row in cctv.head(10).iterrows():
            title = str(row.get('title', row.get('标题', '')))
            cctv_titles.append(title)
            print(f"  📺 {title[:60]}")
        results['_cctv'] = {'titles': cctv_titles}
except Exception as e:
    print(f"  ❌ CCTV: {e}")
    results['_cctv'] = {'error': str(e)[:100]}

# Save
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\n✅ 舆情扫描完成，数据已保存至 {output_path}")

#!/usr/bin/env python3
"""Sentiment analysis for portfolio adjustment - 2026-03-06"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Use akshare for news
try:
    import akshare as ak
except ImportError:
    print("ERROR: akshare not installed")
    sys.exit(1)

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '5G', '通信', '机器人',
    '两会', '红利', '有色金属', '港股', '恒生科技', '电力',
    '化工', '航空', '国防', '白银'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨',
                      '拉升', '涨停', '反弹', '回升', '攀升', '领涨', '走高',
                      '飙升', '暴涨', '新高', '加速', '扩张', '利多']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '大跌',
                      '跌停', '下挫', '暴雷', '走低', '重挫', '恶化', '下行',
                      '萎缩', '崩盘', '熊市', '抛售', '低迷', '退市']

    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)

    if pos_count > neg_count:
        return "positive", pos_count, neg_count
    elif neg_count > pos_count:
        return "negative", pos_count, neg_count
    else:
        return "neutral", pos_count, neg_count

results = {}

for keyword in KEYWORDS:
    print(f"Scanning '{keyword}'...")
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is not None and not news.empty:
            top_news = news.head(5)
            articles = []
            pos_count = 0
            neg_count = 0
            neu_count = 0

            for _, row in top_news.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                source = str(row.get('文章来源', row.get('source', '')))
                pub_date = str(row.get('发布时间', row.get('publish_time', '')))

                sentiment, p, n = simple_sentiment(title + content)
                if sentiment == 'positive':
                    pos_count += 1
                elif sentiment == 'negative':
                    neg_count += 1
                else:
                    neu_count += 1

                articles.append({
                    'title': title[:100],
                    'source': source,
                    'date': pub_date,
                    'sentiment': sentiment
                })

            # Overall sentiment
            if pos_count > neg_count:
                overall = 'positive'
            elif neg_count > pos_count:
                overall = 'negative'
            else:
                overall = 'neutral'

            results[keyword] = {
                'overall_sentiment': overall,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'articles': articles
            }
            print(f"  {overall} (pos={pos_count}, neg={neg_count}, neu={neu_count})")
        else:
            results[keyword] = {'overall_sentiment': 'no_data', 'articles': []}
            print(f"  No data")
    except Exception as e:
        print(f"  ERROR: {e}")
        results[keyword] = {'overall_sentiment': 'error', 'error': str(e), 'articles': []}

# Also fetch CCTV news and macro news
print("\nFetching CCTV news...")
try:
    cctv = ak.news_cctv(date='20260305')
    if cctv is not None and not cctv.empty:
        cctv_items = []
        for _, row in cctv.head(10).iterrows():
            cctv_items.append({
                'title': str(row.get('title', '')),
                'date': str(row.get('date', ''))
            })
        results['_cctv_news'] = cctv_items
        print(f"  Got {len(cctv_items)} items")
except Exception as e:
    print(f"  CCTV error: {e}")
    results['_cctv_news'] = []

print("\nFetching economic news (Baidu)...")
try:
    econ = ak.news_economic_baidu()
    if econ is not None and not econ.empty:
        econ_items = []
        for _, row in econ.head(10).iterrows():
            title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
            econ_items.append({'title': title})
        results['_economic_news'] = econ_items
        print(f"  Got {len(econ_items)} items")
except Exception as e:
    print(f"  Economic news error: {e}")
    results['_economic_news'] = []

# Save
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\n✅ Sentiment data saved to {output_path}")

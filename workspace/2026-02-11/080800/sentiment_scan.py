#!/usr/bin/env python3
"""
Sentiment Scan - Economic News & Market Sentiment
Date: 2026-02-11
Fetches latest news for key sectors using AkShare
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import akshare as ak
import pandas as pd

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '通信', '5G', '机器人',
    '红利', '港股', '电力', '化工', '豆粕', 'DeepSeek', '春节'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    if not text or not isinstance(text, str):
        return "neutral"
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '走强',
                      '涨停', '大涨', '反弹', '飙升', '暴涨', '新高', '超预期',
                      '加速', '领涨', '拉升', '放量', '利好', '回暖', '复苏',
                      '井喷', '强劲', '活跃', '火爆', '看好']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '走弱',
                      '跌停', '大跌', '崩盘', '暴雷', '亏损', '减持', '退市',
                      '萎缩', '收缩', '恶化', '压力', '担忧', '警惕', '下行']

    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

all_sentiment_data = {}

# 1. Fetch stock news by keyword
print("=" * 60)
print("SENTIMENT SCAN - Keyword-based News")
print("=" * 60)

for keyword in KEYWORDS:
    print(f"\n--- Scanning: {keyword} ---")
    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is not None and len(news_df) > 0:
            # Get top 5 news items
            top_news = news_df.head(5)
            news_items = []

            for _, row in top_news.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                pub_date = str(row.get('发布时间', row.get('publish_time', '')))
                source = str(row.get('文章来源', row.get('source', '')))

                sentiment = simple_sentiment(title + ' ' + content)
                news_items.append({
                    'title': title,
                    'sentiment': sentiment,
                    'date': pub_date,
                    'source': source,
                })
                print(f"  [{sentiment:>8}] {title[:60]}")

            # Aggregate sentiment
            sentiments = [item['sentiment'] for item in news_items]
            pos_count = sentiments.count('positive')
            neg_count = sentiments.count('negative')
            neu_count = sentiments.count('neutral')

            if pos_count > neg_count + neu_count * 0.3:
                overall = 'positive'
            elif neg_count > pos_count + neu_count * 0.3:
                overall = 'negative'
            else:
                overall = 'neutral'

            all_sentiment_data[keyword] = {
                'overall': overall,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'top_news': news_items,
            }
            print(f"  → Overall: {overall} (pos:{pos_count}/neg:{neg_count}/neu:{neu_count})")
        else:
            print(f"  No news found for {keyword}")
            all_sentiment_data[keyword] = {
                'overall': 'neutral',
                'positive': 0, 'negative': 0, 'neutral': 0,
                'top_news': [],
            }
    except Exception as e:
        print(f"  ERROR fetching news for {keyword}: {e}")
        all_sentiment_data[keyword] = {
            'overall': 'unknown',
            'positive': 0, 'negative': 0, 'neutral': 0,
            'top_news': [],
            'error': str(e),
        }

# 2. Fetch general economic news
print("\n" + "=" * 60)
print("GENERAL ECONOMIC NEWS")
print("=" * 60)

try:
    econ_news = ak.news_economic_baidu()
    if econ_news is not None and len(econ_news) > 0:
        econ_items = []
        for _, row in econ_news.head(10).iterrows():
            title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
            content = str(row.get('content', row.iloc[1] if len(row) > 1 else ''))
            sentiment = simple_sentiment(title + ' ' + content)
            econ_items.append({
                'title': title,
                'sentiment': sentiment,
            })
            print(f"  [{sentiment:>8}] {title[:70]}")
        all_sentiment_data['macro_economic'] = {
            'overall': 'mixed',
            'top_news': econ_items,
        }
except Exception as e:
    print(f"  ERROR: {e}")
    all_sentiment_data['macro_economic'] = {'overall': 'unknown', 'error': str(e)}

# 3. Summary
print("\n" + "=" * 60)
print("SENTIMENT SUMMARY")
print("=" * 60)

for keyword, data in all_sentiment_data.items():
    if keyword == 'macro_economic':
        continue
    emoji = '🟢' if data['overall'] == 'positive' else ('🔴' if data['overall'] == 'negative' else '⚪')
    top_title = data['top_news'][0]['title'][:50] if data.get('top_news') else 'N/A'
    print(f"  {emoji} {keyword:<10} {data['overall']:<10} | {top_title}")

# Save results
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_sentiment_data, f, indent=4, ensure_ascii=False)
print(f"\nSentiment data saved to: {output_path}")

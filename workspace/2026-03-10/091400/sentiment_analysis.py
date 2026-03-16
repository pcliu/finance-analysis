#!/usr/bin/env python3
"""
Sentiment Analysis - 2026-03-10
Scans economic sentiment from AkShare + web for key sectors
"""
import sys
import os
import json
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Simple sentiment function
positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '涨停', '暴涨', '反弹', 
                  '拉升', '飙升', '走高', '新高', '放量', '加速', '超预期', '国产替代', '突围', '爆发',
                  '净流入', '加仓', '增持', '回暖', '复苏', '利多']
negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停', '大跌', '走低', '破位',
                  '减持', '净流出', '回调', '下挫', '崩盘', '恐慌', '减仓', '抛售', '制裁', '贸易战',
                  '关税', '冲突', '紧张']

def simple_sentiment(text):
    if not text:
        return "neutral"
    pos = sum(1 for w in positive_words if w in text)
    neg = sum(1 for w in negative_words if w in text)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"

import akshare as ak

keywords = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土', '黄金',
    '航天', '科创', '机器人', '5G', '两会', '电力', '化工', '红利', 
    '有色金属', '白银', '航空', '国防', '恒生科技', '港股', '通信',
    '关税', '贸易战', '特朗普'
]

all_sentiment = {}

for kw in keywords:
    try:
        print(f"Fetching news for: {kw}")
        news = ak.stock_news_em(symbol=kw)
        if news is not None and len(news) > 0:
            top_news = news.head(5)
            articles = []
            pos_count = 0
            neg_count = 0
            neu_count = 0
            for _, row in top_news.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                s = simple_sentiment(title + ' ' + content)
                articles.append({
                    'title': title,
                    'sentiment': s,
                    'source': str(row.get('文章来源', row.get('source', '')))
                })
                if s == 'positive':
                    pos_count += 1
                elif s == 'negative':
                    neg_count += 1
                else:
                    neu_count += 1
            
            if pos_count > neg_count:
                overall = "偏多"
            elif neg_count > pos_count:
                overall = "偏空"
            else:
                overall = "中性"
            
            all_sentiment[kw] = {
                'overall': overall,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'articles': articles
            }
            print(f"  → {overall} (正{pos_count}/负{neg_count}/中{neu_count})")
        else:
            print(f"  → No news data")
            all_sentiment[kw] = {'overall': '无数据', 'positive': 0, 'negative': 0, 'neutral': 0, 'articles': []}
        
        time.sleep(0.3)
    except Exception as e:
        print(f"  ERROR: {e}")
        all_sentiment[kw] = {'overall': '获取失败', 'positive': 0, 'negative': 0, 'neutral': 0, 'articles': [], 'error': str(e)}

# Also get CCTV news
try:
    print("\nFetching CCTV news...")
    cctv = ak.news_cctv(date="20260309")
    cctv_articles = []
    if cctv is not None and len(cctv) > 0:
        for _, row in cctv.head(10).iterrows():
            title = str(row.get('title', ''))
            cctv_articles.append(title)
            print(f"  • {title}")
    all_sentiment['_cctv_news'] = cctv_articles
except Exception as e:
    print(f"  CCTV news error: {e}")
    all_sentiment['_cctv_news'] = []

# Also get general economic news
try:
    print("\nFetching economic news...")
    econ = ak.news_economic_baidu()
    econ_articles = []
    if econ is not None and len(econ) > 0:
        for _, row in econ.head(10).iterrows():
            title = str(row.get('title', ''))
            econ_articles.append(title)
            print(f"  • {title}")
    all_sentiment['_economic_news'] = econ_articles
except Exception as e:
    print(f"  Economic news error: {e}")
    all_sentiment['_economic_news'] = []

# Save
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(all_sentiment, f, indent=4, ensure_ascii=False)

print(f"\n✅ Sentiment analysis complete! {len(keywords)} keywords scanned.")
print(f"📁 Data saved to: {output_path}")

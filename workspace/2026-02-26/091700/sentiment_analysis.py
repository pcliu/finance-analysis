#!/usr/bin/env python3
"""Sentiment analysis for portfolio adjustment - 2026-02-26 盘前"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '红利', '通信', '5G', '6G',
    '机器人', '电网', '电力', '有色', '白银', '港股', '化工',
    '豆粕', '矿业', '航空', '卫星'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', 
                      '暴涨', '拉升', '走强', '领涨', '反弹', '回暖', '复苏',
                      '加速', '超预期', '涨停', '新高', '催化', '提振']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '大跌',
                      '回调', '重挫', '走弱', '承压', '下行', '崩', '跌停',
                      '萎缩', '寒冬', '减持', '退市', '危机', '抛售']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

results = {}

try:
    import akshare as ak
    
    for keyword in KEYWORDS:
        print(f"Scanning sentiment for: {keyword}...")
        try:
            news = ak.stock_news_em(symbol=keyword)
            if news is not None and not news.empty:
                top_news = news.head(5)
                sentiment_list = []
                for _, row in top_news.iterrows():
                    title = str(row.get('新闻标题', row.get('title', '')))
                    content = str(row.get('新闻内容', row.get('content', title)))
                    source = str(row.get('文章来源', row.get('source', '')))
                    pub_time = str(row.get('发布时间', row.get('publish_time', '')))
                    
                    sent = simple_sentiment(title + ' ' + content)
                    sentiment_list.append({
                        'title': title,
                        'sentiment': sent,
                        'source': source,
                        'time': pub_time,
                    })
                
                pos_count = sum(1 for s in sentiment_list if s['sentiment'] == 'positive')
                neg_count = sum(1 for s in sentiment_list if s['sentiment'] == 'negative')
                neu_count = sum(1 for s in sentiment_list if s['sentiment'] == 'neutral')
                
                if pos_count > neg_count + 1:
                    overall = '强势偏多'
                elif pos_count > neg_count:
                    overall = '偏多'
                elif neg_count > pos_count + 1:
                    overall = '强势偏空'
                elif neg_count > pos_count:
                    overall = '偏空'
                else:
                    overall = '中性'
                
                results[keyword] = {
                    'overall': overall,
                    'positive': pos_count,
                    'negative': neg_count,
                    'neutral': neu_count,
                    'news': sentiment_list
                }
                
                print(f"  {overall} (P:{pos_count}/N:{neg_count}/U:{neu_count})")
            else:
                results[keyword] = {
                    'overall': '无数据',
                    'positive': 0, 'negative': 0, 'neutral': 0,
                    'news': []
                }
                print(f"  No data available")
        except Exception as e:
            print(f"  Error: {e}")
            results[keyword] = {
                'overall': '获取失败',
                'positive': 0, 'negative': 0, 'neutral': 0,
                'news': [], 'error': str(e)
            }

except ImportError:
    print("akshare not available, using web search fallback")
    # Results will be empty, supplemented by web search

# Also try to get general economic news
try:
    import akshare as ak
    print("\nFetching general economic news...")
    try:
        econ_news = ak.news_economic_baidu()
        if econ_news is not None and not econ_news.empty:
            general_news = []
            for _, row in econ_news.head(10).iterrows():
                title = str(row.get('title', row.get('新闻标题', '')))
                general_news.append({
                    'title': title,
                    'sentiment': simple_sentiment(title)
                })
            results['_general_economic'] = general_news
            print(f"  Got {len(general_news)} general economic news items")
    except Exception as e:
        print(f"  Could not fetch economic news: {e}")
except ImportError:
    pass

# Save results
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=4, ensure_ascii=False)

print(f"\nSentiment analysis complete. Results saved to {output_path}")
print(f"Keywords analyzed: {len([k for k in results if not k.startswith('_')])}/{len(KEYWORDS)}")

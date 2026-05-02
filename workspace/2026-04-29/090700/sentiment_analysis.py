#!/usr/bin/env python3
"""
Sentiment Analysis Script — 2026-04-29
Fetches news and sentiment for key sectors using AkShare.
"""
import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add skill path
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)
from scripts.utils import make_serializable

import akshare as ak

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '化工', '电力', '5G',
    '机器人', '红利', '油价', '新能源'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring."""
    if not text or not isinstance(text, str):
        return 'neutral'
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '涨停',
                      '回暖', '反弹', '加速', '提升', '扩大', '景气', '超预期', '放量',
                      '飙升', '新高', '看好', '看涨', '复苏', '繁荣', '推进', '加码']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停', '大跌',
                      '回落', '走弱', '萎缩', '下滑', '承压', '低迷', '不及预期', '缩量',
                      '暴雷', '亏损', '减持', '抛售', '制裁', '封锁', '战争', '冲突']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'


def fetch_keyword_news(keyword, max_items=8):
    """Fetch news for a keyword from East Money."""
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is not None and len(news) > 0:
            items = []
            for _, row in news.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                publish_time = str(row.get('发布时间', row.get('publish_time', '')))
                source = str(row.get('文章来源', row.get('source', '')))
                sentiment = simple_sentiment(title + ' ' + content)
                items.append({
                    'title': title,
                    'time': publish_time,
                    'source': source,
                    'sentiment': sentiment
                })
            return items
    except Exception as e:
        print(f"   ⚠️ Error fetching news for '{keyword}': {e}")
    return []


def main():
    print("=" * 60)
    print("Sentiment Analysis — 2026-04-29")
    print("=" * 60)
    
    all_sentiment = {}
    
    # Fetch news for each keyword
    for keyword in KEYWORDS:
        print(f"\n🔍 Scanning: {keyword}...")
        news_items = fetch_keyword_news(keyword)
        
        if news_items:
            pos = sum(1 for n in news_items if n['sentiment'] == 'positive')
            neg = sum(1 for n in news_items if n['sentiment'] == 'negative')
            neu = sum(1 for n in news_items if n['sentiment'] == 'neutral')
            
            if pos > neg:
                overall = 'positive'
            elif neg > pos:
                overall = 'negative'
            else:
                overall = 'neutral'
            
            all_sentiment[keyword] = {
                'overall_sentiment': overall,
                'positive_count': pos,
                'negative_count': neg,
                'neutral_count': neu,
                'total_articles': len(news_items),
                'top_headlines': [n['title'] for n in news_items[:5]],
                'articles': news_items
            }
            print(f"   📰 {len(news_items)} articles | Sentiment: {overall} (P:{pos}/N:{neg}/U:{neu})")
        else:
            all_sentiment[keyword] = {
                'overall_sentiment': 'no_data',
                'articles': []
            }
            print(f"   ❌ No news found")
    
    # Try to fetch economic news from Baidu
    print("\n\n📰 Fetching Baidu Economic News...")
    baidu_news = []
    try:
        econ = ak.news_economic_baidu()
        if econ is not None and len(econ) > 0:
            for _, row in econ.head(15).iterrows():
                title = str(row.get('title', ''))
                content = str(row.get('content', row.get('description', '')))
                baidu_news.append({
                    'title': title,
                    'sentiment': simple_sentiment(title + ' ' + content)
                })
            print(f"   ✅ Got {len(baidu_news)} economic news items")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
    
    # Save results
    output = {
        'analysis_date': '2026-04-29',
        'keyword_sentiment': all_sentiment,
        'baidu_economic_news': baidu_news,
    }
    
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(make_serializable(output), f, indent=2, ensure_ascii=False)
    print(f"\n✅ Sentiment data saved to {output_path}")


if __name__ == '__main__':
    main()

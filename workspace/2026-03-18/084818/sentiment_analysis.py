#!/usr/bin/env python3
"""
Sentiment Analysis — 2026-03-18
Scan key financial keywords for latest news and sentiment
"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
    import pandas as pd
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '红利', '5G', '通信',
    '机器人', '化工', '航空', '电力', '港股', '恒生科技',
    '石油', '有色金属', '钼', '铜', '中东', '特朗普',
    '关税', '贸易战', '两会', '白银', '国防'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring."""
    if not isinstance(text, str):
        return "neutral"
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '涨停',
                      '反弹', '走强', '回暖', '看好', '加速', '暴涨', '飙升', '新高']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '走弱', '跌停',
                      '回调', '承压', '萎缩', '抛售', '崩盘', '重挫', '下滑', '暴跌']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def fetch_news_for_keyword(keyword, max_items=5):
    """Fetch news for a keyword using AkShare."""
    results = []
    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is not None and not news_df.empty:
            for _, row in news_df.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', title)))
                source = str(row.get('文章来源', row.get('source', '')))
                pub_time = str(row.get('发布时间', row.get('publish_time', '')))
                
                sentiment = simple_sentiment(title + ' ' + content)
                results.append({
                    'title': title[:100],
                    'sentiment': sentiment,
                    'source': source,
                    'time': pub_time,
                })
    except Exception as e:
        results.append({'error': str(e)[:200]})
    return results

def fetch_cctv_news():
    """Fetch CCTV news headlines."""
    results = []
    try:
        cctv_df = ak.news_cctv()
        if cctv_df is not None and not cctv_df.empty:
            for _, row in cctv_df.head(10).iterrows():
                title = str(row.get('title', ''))
                results.append(title)
    except Exception as e:
        results.append(f'Error: {str(e)[:200]}')
    return results

def fetch_economic_news():
    """Fetch Baidu economic news."""
    results = []
    try:
        econ_df = ak.news_economic_baidu()
        if econ_df is not None and not econ_df.empty:
            for _, row in econ_df.head(10).iterrows():
                title = str(row.get('title', ''))
                content = str(row.get('content', title))
                sentiment = simple_sentiment(title + ' ' + content)
                results.append({
                    'title': title[:200],
                    'sentiment': sentiment,
                })
    except Exception as e:
        results.append({'error': str(e)[:200]})
    return results


def main():
    print("=" * 60)
    print("Sentiment Analysis — 2026-03-18")
    print("=" * 60)
    
    all_sentiment = {}
    
    # Scan all keywords
    total = len(KEYWORDS)
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{i}/{total}] Scanning: {keyword}...")
        news_items = fetch_news_for_keyword(keyword)
        
        pos = sum(1 for n in news_items if n.get('sentiment') == 'positive')
        neg = sum(1 for n in news_items if n.get('sentiment') == 'negative')
        neu = sum(1 for n in news_items if n.get('sentiment') == 'neutral')
        
        if pos > neg:
            overall = '偏多'
            if pos >= 3:
                overall = '强偏多'
        elif neg > pos:
            overall = '偏空'
            if neg >= 3:
                overall = '强偏空'
        else:
            overall = '中性'
        
        all_sentiment[keyword] = {
            'news': news_items,
            'positive': pos,
            'negative': neg,
            'neutral': neu,
            'overall': overall,
        }
        
        print(f"  {overall} (正:{pos} 负:{neg} 中:{neu})")
        for n in news_items:
            if 'title' in n:
                icon = '🟢' if n.get('sentiment') == 'positive' else ('🔴' if n.get('sentiment') == 'negative' else '⚪')
                print(f"    {icon} {n['title'][:80]}")
    
    # Fetch CCTV news
    print("\n\n--- CCTV 新闻联播 ---")
    cctv = fetch_cctv_news()
    for title in cctv:
        print(f"  📺 {title}")
    
    # Fetch economic news
    print("\n\n--- 百度财经新闻 ---")
    econ = fetch_economic_news()
    for item in econ:
        if isinstance(item, dict) and 'title' in item:
            icon = '🟢' if item.get('sentiment') == 'positive' else ('🔴' if item.get('sentiment') == 'negative' else '⚪')
            print(f"  {icon} {item['title'][:100]}")
    
    # Save data
    output = {
        'keywords': all_sentiment,
        'cctv': cctv,
        'economic_news': econ,
        'scan_date': '2026-03-18 08:48',
    }
    
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ Sentiment data saved to: {output_path}")


if __name__ == '__main__':
    main()

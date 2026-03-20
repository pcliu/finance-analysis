#!/usr/bin/env python3
"""
Sentiment Analysis Script — 2026-03-17
Fetches news and sentiment data for key sectors and keywords
"""

import sys
import os
import json
import traceback
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to scan
KEYWORDS = [
    '消费', '红利', '医疗', '军工', '光伏', 'AI', '半导体', '科技',
    '5G', '通信', '化工', '航空', '航天', '机器人', '科创',
    '黄金', '白银', '稀土', '有色金属', '电力', '港股', '恒生科技',
    '关税', '贸易战', '两会', '国防', '石油', '中东', '特朗普'
]

# Simple keyword-based sentiment
POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '走强', '大涨',
                  '暴涨', '涨停', '反弹', '回暖', '加速', '新高', '领涨', '拉升',
                  '飙升', '净流入', '看好', '景气', '超预期', '放量', '活跃']
NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '走弱', '跌停',
                  '回落', '下挫', '承压', '净流出', '看空', '萎缩', '低迷', '破位',
                  '缩量', '减持', '爆雷', '遇冷', '收缩', '触及跌停', '跌超']

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    if not text:
        return 'neutral', 0, 0
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text)
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text)
    if pos_count > neg_count:
        return 'positive', pos_count, neg_count
    elif neg_count > pos_count:
        return 'negative', pos_count, neg_count
    else:
        return 'neutral', pos_count, neg_count

def fetch_keyword_news(keyword, max_items=5):
    """Fetch news for a keyword using akshare"""
    try:
        import akshare as ak
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is None or news_df.empty:
            return []
        
        results = []
        columns = news_df.columns.tolist()
        
        for _, row in news_df.head(max_items).iterrows():
            title = ''
            content = ''
            source = ''
            pub_time = ''
            
            for col in columns:
                col_lower = str(col).lower()
                val = str(row[col]) if row[col] is not None else ''
                if '标题' in col_lower or 'title' in col_lower or col == '新闻标题':
                    title = val
                elif '内容' in col_lower or 'content' in col_lower or col == '新闻内容':
                    content = val
                elif '来源' in col_lower or 'source' in col_lower or col == '文章来源':
                    source = val
                elif '时间' in col_lower or 'date' in col_lower or 'time' in col_lower or col == '发布时间':
                    pub_time = val
            
            # If no title found, use first column
            if not title and len(columns) > 0:
                title = str(row[columns[0]])
            
            combined_text = f"{title} {content}"
            sentiment, pos, neg = simple_sentiment(combined_text)
            
            results.append({
                'title': title[:200],
                'content': content[:300] if content else '',
                'source': source,
                'time': pub_time,
                'sentiment': sentiment,
                'pos_count': pos,
                'neg_count': neg,
            })
        
        return results
    except Exception as e:
        return [{'error': str(e)}]

def fetch_cctv_news():
    """Fetch latest CCTV news"""
    try:
        import akshare as ak
        news_df = ak.news_cctv()
        if news_df is None or news_df.empty:
            return []
        
        results = []
        for _, row in news_df.head(10).iterrows():
            title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
            content = str(row.get('content', ''))
            results.append({
                'title': title[:200],
                'content': content[:200],
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]

def fetch_economic_news():
    """Fetch Baidu economic news"""
    try:
        import akshare as ak
        news_df = ak.news_economic_baidu()
        if news_df is None or news_df.empty:
            return []
        
        results = []
        for _, row in news_df.head(10).iterrows():
            title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
            content = str(row.get('content', row.get('description', '')))
            combined = f"{title} {content}"
            sentiment, pos, neg = simple_sentiment(combined)
            results.append({
                'title': title[:200],
                'content': str(content)[:200],
                'sentiment': sentiment,
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def main():
    print("=" * 60)
    print("Sentiment Analysis — 2026-03-17")
    print("=" * 60)
    
    all_sentiment = {}
    
    # 1. Scan all keywords
    total = len(KEYWORDS)
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{i}/{total}] Scanning: {keyword}...")
        news = fetch_keyword_news(keyword, max_items=5)
        
        if news and 'error' not in news[0]:
            pos_count = sum(1 for n in news if n.get('sentiment') == 'positive')
            neg_count = sum(1 for n in news if n.get('sentiment') == 'negative')
            neu_count = sum(1 for n in news if n.get('sentiment') == 'neutral')
            
            if pos_count > neg_count + 1:
                overall = '强偏多' if pos_count >= 4 else '偏多'
            elif neg_count > pos_count + 1:
                overall = '强偏空' if neg_count >= 4 else '偏空'
            elif pos_count > neg_count:
                overall = '偏多'
            elif neg_count > pos_count:
                overall = '偏空'
            else:
                overall = '中性'
            
            all_sentiment[keyword] = {
                'news': news,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'overall': overall,
            }
            print(f"  → {overall} (正:{pos_count}/负:{neg_count}/中:{neu_count})")
            for n in news[:3]:
                print(f"    [{n.get('sentiment', '?')}] {n.get('title', 'N/A')[:60]}")
        else:
            error_msg = news[0].get('error', 'Unknown') if news else 'No data'
            all_sentiment[keyword] = {
                'news': [],
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'overall': '无数据',
                'error': error_msg,
            }
            print(f"  ⚠️ Error: {error_msg[:80]}")
    
    # 2. CCTV News
    print(f"\n[Extra] Fetching CCTV news...")
    cctv = fetch_cctv_news()
    if cctv and 'error' not in cctv[0]:
        print(f"  Got {len(cctv)} items")
        for item in cctv[:5]:
            print(f"    • {item.get('title', 'N/A')[:60]}")
    
    # 3. Economic News
    print(f"\n[Extra] Fetching economic news...")
    economic = fetch_economic_news()
    if economic and 'error' not in economic[0]:
        print(f"  Got {len(economic)} items")
        for item in economic[:5]:
            print(f"    [{item.get('sentiment', '?')}] {item.get('title', 'N/A')[:60]}")
    
    # Save output
    output = {
        'timestamp': '2026-03-17T08:39:37+08:00',
        'keywords_sentiment': all_sentiment,
        'cctv_news': cctv,
        'economic_news': economic,
    }
    
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    print(f"\n✅ Sentiment data saved to: {output_path}")


if __name__ == '__main__':
    main()

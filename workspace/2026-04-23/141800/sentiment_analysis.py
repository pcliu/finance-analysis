#!/usr/bin/env python3
"""
Sentiment data collection — 2026-04-23
Fetches news and sentiment for key market keywords.
"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to monitor
KEYWORDS = [
    "AI", "算力", "5G", "芯片", "半导体", "消费",
    "医疗", "军工", "光伏", "化工", "电力",
    "有色", "稀土", "黄金", "机器人", "科创",
    "中美贸易", "伊朗", "红利", "航天"
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring."""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '暴涨', '反弹',
                      '回升', '领涨', '活跃', '景气', '加速', '放量', '涨停', '飙升', '走强',
                      '井喷', '爆发', '牛市', '升级', '提振', '催化']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回调', '减持', '下行',
                      '缩量', '跌停', '走弱', '承压', '恶化', '萎缩', '下滑', '亏损', '制裁',
                      '冲突', '战争', '封锁', '抛售']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count + 1:
        return "positive"
    elif neg_count > pos_count + 1:
        return "negative"
    elif pos_count > neg_count:
        return "slightly_positive"
    elif neg_count > pos_count:
        return "slightly_negative"
    else:
        return "neutral"


def fetch_keyword_news(keyword, max_items=8):
    """Fetch news for a keyword using akshare."""
    import akshare as ak
    
    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is None or len(news_df) == 0:
            return []
        
        results = []
        for i, row in news_df.head(max_items).iterrows():
            title = str(row.get('新闻标题', row.get('title', '')))
            content = str(row.get('新闻内容', row.get('content', '')))
            source = str(row.get('文章来源', row.get('source', '')))
            pub_date = str(row.get('发布时间', row.get('publish_time', '')))
            
            text = title + ' ' + content
            sentiment = simple_sentiment(text)
            
            results.append({
                'title': title,
                'source': source,
                'date': pub_date,
                'sentiment': sentiment
            })
        
        return results
    except Exception as e:
        print(f"  ⚠️ Error fetching news for '{keyword}': {e}")
        return []


def get_economic_news():
    """Fetch general economic news."""
    import akshare as ak
    
    results = []
    try:
        news = ak.news_economic_baidu()
        if news is not None and len(news) > 0:
            for i, row in news.head(10).iterrows():
                title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
                results.append({
                    'title': title,
                    'source': 'baidu_economic',
                    'sentiment': simple_sentiment(title)
                })
    except Exception as e:
        print(f"  ⚠️ Error fetching economic news: {e}")
    
    return results


def main():
    print("=" * 80)
    print("Sentiment Data Collection — 2026-04-23")
    print("=" * 80)
    
    all_sentiment = {}
    
    # Fetch keyword-specific news
    for kw in KEYWORDS:
        print(f"  Fetching news for: {kw}...")
        news = fetch_keyword_news(kw, max_items=5)
        
        if news:
            sentiments = [n['sentiment'] for n in news]
            pos = sum(1 for s in sentiments if 'positive' in s)
            neg = sum(1 for s in sentiments if 'negative' in s)
            neu = len(sentiments) - pos - neg
            
            if pos > neg + 1:
                overall = "positive"
            elif neg > pos + 1:
                overall = "negative"
            elif pos > neg:
                overall = "slightly_positive"
            elif neg > pos:
                overall = "slightly_negative"
            else:
                overall = "neutral"
            
            all_sentiment[kw] = {
                'overall': overall,
                'positive_count': pos,
                'negative_count': neg,
                'neutral_count': neu,
                'top_headlines': [n['title'] for n in news[:3]],
                'details': news
            }
            print(f"    → {overall} (pos={pos}, neg={neg}, neu={neu})")
            for n in news[:2]:
                print(f"      📰 {n['title'][:60]}...")
        else:
            all_sentiment[kw] = {
                'overall': 'no_data',
                'top_headlines': [],
                'details': []
            }
            print(f"    → no data")
    
    # Fetch economic news
    print("\n  Fetching general economic news...")
    econ_news = get_economic_news()
    all_sentiment['economic_general'] = {
        'headlines': [n['title'] for n in econ_news],
        'details': econ_news
    }
    
    # Save results
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_sentiment, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Sentiment data saved to {output_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print("Sentiment Summary")
    print("-" * 80)
    for kw, data in all_sentiment.items():
        if kw == 'economic_general':
            continue
        overall = data.get('overall', 'N/A')
        emoji = {'positive': '🟢🟢', 'slightly_positive': '🟢', 'neutral': '🟡',
                 'slightly_negative': '🟡🔴', 'negative': '🔴🔴', 'no_data': '⚪'}.get(overall, '❓')
        headline = data.get('top_headlines', [''])[0][:50] if data.get('top_headlines') else ''
        print(f"  {emoji} {kw:<12} → {overall:<20} | {headline}")
    print("=" * 80)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Sentiment Analysis — 2026-04-27
Fetches news and sentiment for key market keywords using AkShare
"""

import sys
import os
import json
import traceback
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土',
    '黄金', '航天', '科创', '5G', '算力', '机器人', '化工', '电力',
    '红利', '有色', '伊朗', '中美贸易'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring."""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '拉升',
                      '涨停', '爆发', '活跃', '走强', '反弹', '新高', '暴涨',
                      '飙升', '回升', '看好', '景气', '加速', '扩张', '超预期']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停',
                      '回调', '下挫', '走低', '暴雷', '亏损', '萎缩', '下滑',
                      '承压', '减持', '退市', '低迷', '收缩', '衰退', '制裁']

    pos_count = sum(1 for word in positive_words if word in str(text))
    neg_count = sum(1 for word in negative_words if word in str(text))

    if pos_count > neg_count:
        return "positive", pos_count, neg_count
    elif neg_count > pos_count:
        return "negative", pos_count, neg_count
    else:
        return "neutral", pos_count, neg_count


def fetch_keyword_news(keyword, max_items=8):
    """Fetch news for a single keyword from East Money."""
    import akshare as ak

    result = {
        'keyword': keyword,
        'articles': [],
        'sentiment_summary': 'neutral',
        'positive_count': 0,
        'negative_count': 0,
        'neutral_count': 0,
        'error': None,
    }

    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is not None and len(news_df) > 0:
            news_df = news_df.head(max_items)
            sentiments = []
            for _, row in news_df.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                source = str(row.get('文章来源', row.get('source', '')))
                pub_date = str(row.get('发布时间', row.get('publish_time', '')))

                combined = title + ' ' + content
                sentiment, pos, neg = simple_sentiment(combined)
                sentiments.append(sentiment)

                result['articles'].append({
                    'title': title,
                    'source': source,
                    'date': pub_date,
                    'sentiment': sentiment,
                })

            result['positive_count'] = sentiments.count('positive')
            result['negative_count'] = sentiments.count('negative')
            result['neutral_count'] = sentiments.count('neutral')

            total = len(sentiments)
            if result['positive_count'] > result['negative_count'] + 1:
                result['sentiment_summary'] = 'positive'
            elif result['negative_count'] > result['positive_count'] + 1:
                result['sentiment_summary'] = 'negative'
            elif result['positive_count'] > result['negative_count']:
                result['sentiment_summary'] = 'slightly_positive'
            elif result['negative_count'] > result['positive_count']:
                result['sentiment_summary'] = 'slightly_negative'
            else:
                result['sentiment_summary'] = 'neutral'
    except Exception as e:
        result['error'] = f"{type(e).__name__}: {str(e)}"
        print(f"  Error fetching '{keyword}': {e}")

    return result


def fetch_macro_news():
    """Fetch general economic news from Baidu."""
    import akshare as ak
    results = []
    try:
        news = ak.news_economic_baidu()
        if news is not None and len(news) > 0:
            for _, row in news.head(15).iterrows():
                title = str(row.get('title', ''))
                sentiment, _, _ = simple_sentiment(title)
                results.append({
                    'title': title,
                    'sentiment': sentiment,
                })
    except Exception as e:
        print(f"  Macro news error: {e}")
    return results


def main():
    all_results = {}

    print("=" * 60)
    print(f"Sentiment scan started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # Scan all keywords
    for keyword in KEYWORDS:
        print(f"\n>>> Scanning: {keyword}")
        res = fetch_keyword_news(keyword)
        all_results[keyword] = res
        if res.get('error'):
            print(f"    ERROR: {res['error']}")
        else:
            emoji = {'positive': '🟢', 'slightly_positive': '🟢', 'negative': '🔴',
                     'slightly_negative': '🔴', 'neutral': '🟡'}
            s = res['sentiment_summary']
            print(f"    {emoji.get(s, '🟡')} {s} | +{res['positive_count']} / -{res['negative_count']} / ={res['neutral_count']}")
            for art in res['articles'][:3]:
                print(f"      • {art['title'][:60]}... [{art['sentiment']}]")

    # Macro news
    print("\n" + "=" * 60)
    print("Macro Economic News (Baidu):")
    print("=" * 60)
    macro = fetch_macro_news()
    all_results['_macro_news'] = macro
    for item in macro:
        emoji = '🟢' if item['sentiment'] == 'positive' else ('🔴' if item['sentiment'] == 'negative' else '🟡')
        print(f"  {emoji} {item['title'][:80]}")

    # Save results
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n✅ Sentiment data saved to {output_path}")

    # Summary table
    print("\n" + "=" * 60)
    print(f"{'Keyword':<12} {'Sentiment':<18} {'+':>3} {'-':>3} {'=':>3} {'Top Title':<50}")
    print("-" * 90)
    for kw in KEYWORDS:
        r = all_results.get(kw, {})
        if r.get('error'):
            print(f"{kw:<12} {'ERROR':<18}")
            continue
        s = r.get('sentiment_summary', 'N/A')
        top = r['articles'][0]['title'][:48] if r.get('articles') else 'N/A'
        print(f"{kw:<12} {s:<18} {r.get('positive_count', 0):>3} {r.get('negative_count', 0):>3} {r.get('neutral_count', 0):>3} {top}")


if __name__ == '__main__':
    main()

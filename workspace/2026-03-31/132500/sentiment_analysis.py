#!/usr/bin/env python3
"""Sentiment Analysis — 2026-03-31"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Simple sentiment analysis function
def simple_sentiment(text):
    """Keyword-based sentiment scoring."""
    if not text:
        return "neutral"
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '反弹', '大涨',
                      '上攻', '走强', '放量', '活跃', '涨停', '新高', '飙升', '暴涨',
                      '加速', '景气', '回升', '修复', '领涨', '受益', '催化', '提振',
                      '超预期', '利多', '牛市', '红盘']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回调', '大跌',
                      '破位', '走弱', '缩量', '低迷', '跌停', '新低', '下挫', '承压',
                      '减弱', '萎缩', '衰退', '恶化', '领跌', '拖累', '冲击', '抛售',
                      '利淡', '熊市', '绿盘', '下行']

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


def fetch_news_for_keywords(keywords):
    """Fetch news for each keyword using AkShare."""
    import akshare as ak
    all_results = {}

    for keyword in keywords:
        try:
            print(f"  Fetching news for '{keyword}'...")
            news_df = ak.stock_news_em(symbol=keyword)
            if news_df is not None and not news_df.empty:
                articles = []
                for i, row in news_df.head(8).iterrows():
                    title = str(row.get('新闻标题', ''))
                    content = str(row.get('新闻内容', ''))
                    source = str(row.get('文章来源', ''))
                    pub_date = str(row.get('发布时间', ''))
                    
                    sentiment = simple_sentiment(title + ' ' + content)
                    articles.append({
                        'title': title,
                        'source': source,
                        'date': pub_date,
                        'sentiment': sentiment,
                        'content_preview': content[:200] if content else ''
                    })

                # Overall sentiment for this keyword
                sentiments = [a['sentiment'] for a in articles]
                pos = sum(1 for s in sentiments if 'positive' in s)
                neg = sum(1 for s in sentiments if 'negative' in s)
                if pos > neg + 1:
                    overall = 'positive'
                elif neg > pos + 1:
                    overall = 'negative'
                elif pos > neg:
                    overall = 'slightly_positive'
                elif neg > pos:
                    overall = 'slightly_negative'
                else:
                    overall = 'neutral'

                all_results[keyword] = {
                    'articles': articles,
                    'overall_sentiment': overall,
                    'positive_count': pos,
                    'negative_count': neg,
                    'total': len(articles)
                }
                print(f"    → {len(articles)} articles, sentiment: {overall}")
            else:
                all_results[keyword] = {'articles': [], 'overall_sentiment': 'no_data', 'total': 0}
                print(f"    → No data")
        except Exception as e:
            all_results[keyword] = {'error': str(e), 'overall_sentiment': 'error'}
            print(f"    → Error: {e}")

    return all_results


def fetch_macro_news():
    """Fetch macro economic news."""
    import akshare as ak
    results = {}

    # Baidu economic news
    try:
        print("  Fetching Baidu economic news...")
        econ_news = ak.news_economic_baidu()
        if econ_news is not None and not econ_news.empty:
            articles = []
            for i, row in econ_news.head(15).iterrows():
                title = str(row.get('title', ''))
                content = str(row.get('content', title))
                articles.append({
                    'title': title,
                    'sentiment': simple_sentiment(title + ' ' + content),
                    'content_preview': content[:200] if content else ''
                })
            results['baidu_economic'] = articles
            print(f"    → {len(articles)} articles")
    except Exception as e:
        results['baidu_economic'] = {'error': str(e)}
        print(f"    → Error: {e}")

    # CCTV news
    try:
        print("  Fetching CCTV news...")
        cctv = ak.news_cctv()
        if cctv is not None and not cctv.empty:
            articles = []
            for i, row in cctv.head(10).iterrows():
                title = str(row.get('title', ''))
                articles.append({
                    'title': title,
                    'sentiment': simple_sentiment(title),
                })
            results['cctv'] = articles
            print(f"    → {len(articles)} articles")
    except Exception as e:
        results['cctv'] = {'error': str(e)}
        print(f"    → Error: {e}")

    return results


def main():
    keywords = [
        '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
        '稀土', '黄金', '航天', '科创', '5G', '电力',
        '化工', '矿业', '电网', '机器人', '白银', '豆粕',
        '红利', '新能源', '芯片', '有色金属', '钼'
    ]

    print("=" * 60)
    print("Sentiment Analysis — 2026-03-31")
    print("=" * 60)

    # Keyword news
    print("\n[1/2] Fetching keyword news...")
    keyword_news = fetch_news_for_keywords(keywords)

    # Macro news
    print("\n[2/2] Fetching macro news...")
    macro_news = fetch_macro_news()

    # Combine
    output = {
        'timestamp': '2026-03-31T13:25:00+08:00',
        'keyword_sentiment': keyword_news,
        'macro_news': macro_news,
    }

    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {output_path}")
    print("Done!")


if __name__ == '__main__':
    main()

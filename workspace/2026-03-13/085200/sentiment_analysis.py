#!/usr/bin/env python3
"""
舆情扫描脚本 — 2026-03-13（盘前）
使用 AkShare 获取关键词新闻并进行简单情绪打分
"""

import sys
import os
import json
import time
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土', '黄金',
    '航天', '科创', '通信', '5G', '红利', '化工', '电力', '机器人', '有色金属',
    '白银', '航空', '国防', '恒生科技', '港股', '特朗普', '关税', '贸易战', '两会'
]

POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '涨停', '大涨',
                  '走强', '飙升', '暴涨', '回升', '反弹', '复苏', '加速', '爆发',
                  '利多', '看好', '积极', '乐观', '超预期', '净流入', '放量',
                  '蓄势', '拉升', '新高', '活跃']

NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停', '大跌',
                  '走低', '走弱', '下挫', '回落', '调整', '承压', '萎缩', '恶化',
                  '利空', '看空', '悲观', '低迷', '不及预期', '净流出', '缩量',
                  '破位', '杀跌', '新低', '抛售', '流出', '冲击']


def simple_sentiment(text):
    """Simple keyword-based sentiment scoring."""
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
    """Fetch news for a keyword using AkShare."""
    import akshare as ak
    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is None or len(news_df) == 0:
            return []

        items = []
        for idx, row in news_df.head(max_items).iterrows():
            title = str(row.get('新闻标题', row.get('title', '')))
            content = str(row.get('新闻内容', row.get('content', '')))
            pub_date = str(row.get('发布时间', row.get('publish_time', '')))
            source = str(row.get('文章来源', row.get('source', '')))

            full_text = f"{title} {content}"
            sentiment, pos, neg = simple_sentiment(full_text)

            items.append({
                'title': title,
                'sentiment': sentiment,
                'pos_count': pos,
                'neg_count': neg,
                'pub_date': pub_date,
                'source': source,
            })
        return items
    except Exception as e:
        print(f"  Error fetching news for '{keyword}': {e}")
        return []


def fetch_cctv_news():
    """Fetch latest CCTV news."""
    import akshare as ak
    try:
        news_df = ak.news_cctv()
        if news_df is None or len(news_df) == 0:
            return []
        items = []
        for idx, row in news_df.head(10).iterrows():
            title = str(row.get('title', ''))
            items.append({'title': title})
        return items
    except Exception as e:
        print(f"Error fetching CCTV news: {e}")
        return []


def fetch_economic_news():
    """Fetch economic news from Baidu."""
    import akshare as ak
    try:
        news_df = ak.news_economic_baidu()
        if news_df is None or len(news_df) == 0:
            return []
        items = []
        for idx, row in news_df.head(10).iterrows():
            title = str(row.get('title', row.get('标题', '')))
            content = str(row.get('content', row.get('内容', '')))
            full_text = f"{title} {content}"
            sentiment, pos, neg = simple_sentiment(full_text)
            items.append({
                'title': title,
                'sentiment': sentiment,
            })
        return items
    except Exception as e:
        print(f"Error fetching economic news: {e}")
        return []


def main():
    results = {
        'keywords': {},
        'cctv_news': [],
        'economic_news': [],
    }

    # Scan each keyword
    for kw in KEYWORDS:
        print(f"Scanning: {kw}...")
        items = fetch_keyword_news(kw, max_items=5)
        pos_count = sum(1 for i in items if i['sentiment'] == 'positive')
        neg_count = sum(1 for i in items if i['sentiment'] == 'negative')
        neu_count = sum(1 for i in items if i['sentiment'] == 'neutral')

        if pos_count > neg_count:
            overall = 'positive'
        elif neg_count > pos_count:
            overall = 'negative'
        else:
            overall = 'neutral'

        results['keywords'][kw] = {
            'overall_sentiment': overall,
            'positive': pos_count,
            'negative': neg_count,
            'neutral': neu_count,
            'articles': items,
        }
        print(f"  → {overall} ({pos_count}/{neg_count}/{neu_count})")
        time.sleep(0.5)  # Rate limiting

    # CCTV News
    print("\nFetching CCTV news...")
    results['cctv_news'] = fetch_cctv_news()

    # Economic news
    print("Fetching economic news...")
    results['economic_news'] = fetch_economic_news()

    # Save results
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    print(f"\nSentiment data saved to {output_path}")


if __name__ == '__main__':
    main()

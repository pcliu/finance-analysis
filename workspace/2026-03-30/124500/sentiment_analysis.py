#!/usr/bin/env python3
"""
Sentiment Analysis Script - 2026-03-30
Fetches market news and sentiment for key sectors
"""
import sys, os, json
import akshare as ak
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '电力', '电网', '5G',
    '新能源', '化工', '矿业', '有色', '钼', '机器人',
    '红利', '港股', '恒生科技', '白银', '豆粕', '粮食',
    '芯片', '铜', '人工智能', '通信',
    '伊朗', '特朗普', '中东', '原油', '战争',
    '央行', '降息', '利率', '贸易战', '关税'
]

POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '暴涨',
                  '反弹', '走高', '涨停', '大涨', '拉升', '回升', '活跃',
                  '修复', '领涨', '飙升', '超预期', '新高', '加速', '扩大',
                  '异动拉升', '放量', '主力流入', '北向资金流入', '抢筹']
NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '崩盘',
                  '跳水', '大跌', '走低', '跌停', '重挫', '承压', '回调',
                  '缩量', '萎缩', '低迷', '恶化', '减持', '利空', '破位',
                  '主力流出', '资金出逃', '恐慌']

def simple_sentiment(text):
    """Enhanced keyword-based sentiment scoring"""
    if not text or not isinstance(text, str):
        return 'neutral', 0
    pos_count = sum(1 for word in POSITIVE_WORDS if word in text)
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in text)
    score = pos_count - neg_count
    if score > 0:
        return 'positive', score
    elif score < 0:
        return 'negative', score
    return 'neutral', 0

def fetch_keyword_news(keyword, max_items=8):
    """Fetch news for a keyword from East Money"""
    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is not None and len(news_df) > 0:
            items = []
            for _, row in news_df.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', title)))
                source = str(row.get('文章来源', row.get('source', '')))
                pub_date = str(row.get('发布时间', row.get('publish_time', '')))
                sentiment, score = simple_sentiment(title + ' ' + content)
                items.append({
                    'title': title,
                    'source': source,
                    'date': pub_date,
                    'sentiment': sentiment,
                    'score': score
                })
            return items
    except Exception as e:
        return [{'error': str(e)}]
    return []

def aggregate_sentiment(items):
    """Aggregate sentiment from news items"""
    if not items or (len(items) == 1 and 'error' in items[0]):
        return 'unknown', 0, 0, 0
    pos = sum(1 for i in items if i.get('sentiment') == 'positive')
    neg = sum(1 for i in items if i.get('sentiment') == 'negative')
    neu = sum(1 for i in items if i.get('sentiment') == 'neutral')
    total = pos + neg + neu
    if total == 0:
        return 'unknown', 0, 0, 0
    if pos > neg * 2:
        overall = 'strong_positive'
    elif pos > neg:
        overall = 'positive'
    elif neg > pos * 2:
        overall = 'strong_negative'
    elif neg > pos:
        overall = 'negative'
    else:
        overall = 'neutral'
    return overall, pos, neg, neu

def main():
    print("=" * 60)
    print("Sentiment Analysis - 2026-03-30")
    print("=" * 60)
    
    results = {}
    
    for kw in KEYWORDS:
        print(f"\nFetching news for: {kw}...")
        items = fetch_keyword_news(kw)
        overall, pos, neg, neu = aggregate_sentiment(items)
        results[kw] = {
            'keyword': kw,
            'overall_sentiment': overall,
            'positive_count': pos,
            'negative_count': neg,
            'neutral_count': neu,
            'total_articles': len(items),
            'top_headlines': [i.get('title', '') for i in items[:5] if 'error' not in i],
            'articles': items
        }
        print(f"  Sentiment: {overall} (P:{pos} N:{neg} U:{neu}) | {len(items)} articles")
        for i in items[:3]:
            if 'error' not in i:
                print(f"    [{i['sentiment']}] {i['title'][:60]}")
    
    # Also try general economic news
    print("\n\nFetching general economic news...")
    try:
        eco_news = ak.news_economic_baidu()
        if eco_news is not None and len(eco_news) > 0:
            eco_items = []
            for _, row in eco_news.head(10).iterrows():
                title = str(row.get('title', ''))
                sentiment, score = simple_sentiment(title)
                eco_items.append({
                    'title': title,
                    'sentiment': sentiment,
                    'score': score
                })
            results['_economic_general'] = {
                'source': 'baidu_economic',
                'articles': eco_items,
                'headlines': [i['title'] for i in eco_items[:5]]
            }
            print(f"  Got {len(eco_items)} economic news items")
    except Exception as e:
        print(f"  Economic news error: {e}")
    
    # Save
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n\nResults saved to {output_path}")
    
    # Summary
    print("\n" + "=" * 80)
    print(f"{'Keyword':<15} {'Sentiment':<18} {'P':>3} {'N':>3} {'U':>3} {'Total':>5}")
    print("-" * 80)
    for kw, r in results.items():
        if kw.startswith('_'):
            continue
        print(f"{kw:<15} {r['overall_sentiment']:<18} {r['positive_count']:>3} {r['negative_count']:>3} "
              f"{r['neutral_count']:>3} {r['total_articles']:>5}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Sentiment Analysis for Portfolio Adjustment — 2026-03-23
Fetches news for key sectors and applies simple sentiment scoring
"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
except ImportError:
    print("ERROR: akshare not installed")
    sys.exit(1)

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土',
    '黄金', '航天', '科创', '5G', '通信', '电力', '红利', '机器人',
    '新能源', '化工', '中东', '港股', '恒生科技', '有色金属',
    '铜', '钼', '白银', '石油', '关税', '贸易战', '特朗普',
    '国防', '航空', '储能', '芯片', '算力'
]

POSITIVE_WORDS = [
    '上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '涨停',
    '拉升', '反弹', '走强', '暴涨', '飙升', '领涨', '新高', '回暖',
    '加速', '爆发', '攀升', '提振', '上扬', '上行', '景气', '扩张',
    '超预期', '增持', '加仓', '买入', '利多', '看好', '乐观', '向好'
]

NEGATIVE_WORDS = [
    '下跌', '暴跌', '利空', '风险', '下调', '疲软', '大跌', '跌停',
    '下挫', '崩盘', '走弱', '跳水', '回落', '低迷', '承压', '减持',
    '破位', '新低', '恐慌', '抛售', '萎缩', '收缩', '下行', '衰退',
    '悲观', '预警', '制裁', '封锁', '打压', '限制', '逆风'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    if not text:
        return 'neutral', 0, 0
    pos_count = sum(1 for word in POSITIVE_WORDS if word in str(text))
    neg_count = sum(1 for word in NEGATIVE_WORDS if word in str(text))
    
    if pos_count > neg_count:
        return 'positive', pos_count, neg_count
    elif neg_count > pos_count:
        return 'negative', pos_count, neg_count
    else:
        return 'neutral', pos_count, neg_count

def fetch_keyword_news(keyword, max_items=5):
    """Fetch news for a keyword from East Money"""
    results = []
    try:
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is not None and len(news_df) > 0:
            for _, row in news_df.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                combined = title + ' ' + content
                sentiment, pos, neg = simple_sentiment(combined)
                results.append({
                    'title': title[:100],
                    'sentiment': sentiment,
                    'positive_count': pos,
                    'negative_count': neg,
                })
    except Exception as e:
        results.append({'error': str(e)[:200]})
    return results

def fetch_cctv_news():
    """Fetch CCTV news headlines"""
    results = []
    try:
        news_df = ak.news_cctv()
        if news_df is not None and len(news_df) > 0:
            for _, row in news_df.head(10).iterrows():
                title = str(row.get('title', row.get('新闻标题', '')))
                results.append(title[:100])
    except Exception as e:
        results.append(f'Error: {str(e)[:100]}')
    return results

def main():
    print("=" * 60)
    print("Sentiment Analysis — 2026-03-23")
    print("=" * 60)
    
    all_sentiment = {}
    
    for i, keyword in enumerate(KEYWORDS, 1):
        print(f"\n[{i}/{len(KEYWORDS)}] Scanning news for: {keyword}")
        news = fetch_keyword_news(keyword)
        
        pos = sum(1 for n in news if n.get('sentiment') == 'positive')
        neg = sum(1 for n in news if n.get('sentiment') == 'negative')
        neu = sum(1 for n in news if n.get('sentiment') == 'neutral')
        
        if pos > neg:
            overall = 'positive'
        elif neg > pos:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        all_sentiment[keyword] = {
            'overall': overall,
            'positive_count': pos,
            'negative_count': neg,
            'neutral_count': neu,
            'news': news,
        }
        
        print(f"  → {overall.upper()} (pos={pos}/neg={neg}/neu={neu})")
    
    # CCTV news
    print("\n[CCTV] Fetching CCTV news...")
    cctv = fetch_cctv_news()
    print(f"  → {len(cctv)} headlines fetched")
    
    output = {
        'date': '2026-03-23',
        'keywords': all_sentiment,
        'cctv_news': cctv,
    }
    
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Sentiment data saved to: {output_path}")

if __name__ == '__main__':
    main()

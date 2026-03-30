#!/usr/bin/env python3
"""Sentiment analysis - fetch news for key sectors"""

import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土',
    '黄金', '航天', '科创', '电力', '5G', '通信', '工程机械',
    '化工', '矿业', '白银', '豆粕', '粮食', '石油', '铜', '有色金属',
    '钼', '机器人', '恒生科技', '港股', '中东', '伊朗', '特朗普',
    '关税', '航空', '电网', '芯片', '算力', 'ETF', '新能源',
    '贸易战', '洛阳钼业', '红利'
]

POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨',
                  '涨停', '反弹', '走强', '活跃', '加速', '超预期', '飙升',
                  '暴涨', '领涨', '拉升', '修复', '回暖', '改善', '提升',
                  '扩大', '新高', '增持', '买入', '推荐']
NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停',
                  '走低', '回调', '下挫', '减持', '抛售', '清仓', '暴雷',
                  '萎缩', '承压', '低迷', '恶化', '下滑', '崩盘', '溢价风险']

def simple_sentiment(text):
    if not text:
        return 'neutral'
    pos = sum(1 for w in POSITIVE_WORDS if w in str(text))
    neg = sum(1 for w in NEGATIVE_WORDS if w in str(text))
    if pos > neg:
        return 'positive'
    elif neg > pos:
        return 'negative'
    return 'neutral'

results = {}

# Using akshare for news
try:
    import akshare as ak

    for kw in KEYWORDS:
        print(f"\nFetching news for: {kw}")
        try:
            news = ak.stock_news_em(symbol=kw)
            if news is not None and len(news) > 0:
                items = []
                sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
                for i, row in news.head(5).iterrows():
                    title = str(row.get('新闻标题', row.get('title', '')))
                    content = str(row.get('新闻内容', row.get('content', '')))
                    pub_time = str(row.get('发布时间', row.get('publish_time', '')))

                    sent = simple_sentiment(title + ' ' + content)
                    sentiments[sent] += 1

                    items.append({
                        'title': title[:100],
                        'time': pub_time,
                        'sentiment': sent
                    })
                    print(f"  [{sent}] {title[:60]}")

                # Overall keyword sentiment
                if sentiments['positive'] > sentiments['negative']:
                    overall = 'positive'
                elif sentiments['negative'] > sentiments['positive']:
                    overall = 'negative'
                else:
                    overall = 'neutral'

                results[kw] = {
                    'overall': overall,
                    'positive_count': sentments['positive'] if 'sentments' in dir() else sentiments['positive'],
                    'negative_count': sentiments['negative'],
                    'neutral_count': sentiments['neutral'],
                    'items': items
                }
                # Fix the typo above
                results[kw]['positive_count'] = sentiments['positive']
            else:
                print(f"  No news found for {kw}")
                results[kw] = {'overall': 'neutral', 'positive_count': 0, 'negative_count': 0, 'neutral_count': 0, 'items': []}
        except Exception as e:
            print(f"  Error fetching {kw}: {e}")
            results[kw] = {'overall': 'unknown', 'error': str(e), 'items': []}

except ImportError:
    print("akshare not available")

# Save results
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n=== Sentiment data saved to {output_path} ===")
print(f"Total keywords scanned: {len(results)}")

#!/usr/bin/env python3
"""
Sentiment Analysis — 2026-04-30
Fetch latest news and sentiment for key sector keywords using AkShare.
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Keywords to scan ──
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI',
    '半导体', '稀土', '黄金', '航天', '科创',
    '化工', '电力', '5G', '机器人', '红利',
    '石油', '新能源'
]

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring."""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', 
                      '暴涨', '反弹', '回升', '放量', '新高', '景气',
                      '加速', '扩产', '提价', '爆发', '飙升', '涨停',
                      '看好', '机遇', '布局', '加码', '超预期']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软',
                      '回落', '缩量', '破位', '跌停', '减持', '亏损',
                      '下降', '萎缩', '担忧', '低迷', '承压', '收缩',
                      '走弱', '恶化', '制裁', '限制', '抛售']
    
    if not text:
        return 'neutral'
    
    pos_count = sum(1 for word in positive_words if word in str(text))
    neg_count = sum(1 for word in negative_words if word in str(text))
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'


def fetch_keyword_news(keyword, max_items=8):
    """Fetch news for a keyword via AkShare stock_news_em."""
    try:
        import akshare as ak
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is None or news_df.empty:
            return []
        
        results = []
        for i, row in news_df.head(max_items).iterrows():
            title = str(row.get('新闻标题', row.get('title', '')))
            content = str(row.get('新闻内容', row.get('content', '')))
            source = str(row.get('文章来源', row.get('source', '')))
            pub_date = str(row.get('发布时间', row.get('publish_time', '')))
            
            sentiment = simple_sentiment(title + ' ' + content)
            results.append({
                'title': title[:100],
                'source': source,
                'date': pub_date,
                'sentiment': sentiment,
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def fetch_economic_news():
    """Fetch general economic news from Baidu."""
    try:
        import akshare as ak
        news_df = ak.news_economic_baidu()
        if news_df is None or news_df.empty:
            return []
        
        results = []
        for i, row in news_df.head(10).iterrows():
            title = str(row.get('title', ''))
            content = str(row.get('content', str(row.get('title', ''))))
            sentiment = simple_sentiment(title + ' ' + content)
            results.append({
                'title': title[:100],
                'sentiment': sentiment,
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]


def main():
    all_sentiment = {'keywords': {}, 'economic_news': [], 'summary': {}}
    
    print("=" * 60)
    print("舆情扫描 — Sentiment Scan")
    print("=" * 60)
    
    for kw in KEYWORDS:
        print(f"\n🔍 扫描关键词: {kw}...")
        news = fetch_keyword_news(kw)
        
        if news and 'error' not in news[0]:
            pos = sum(1 for n in news if n.get('sentiment') == 'positive')
            neg = sum(1 for n in news if n.get('sentiment') == 'negative')
            neu = sum(1 for n in news if n.get('sentiment') == 'neutral')
            total = len(news)
            
            if pos > neg and pos >= total * 0.4:
                overall = 'positive'
            elif neg > pos and neg >= total * 0.4:
                overall = 'negative'
            else:
                overall = 'neutral'
            
            all_sentiment['keywords'][kw] = {
                'news': news,
                'stats': {'positive': pos, 'negative': neg, 'neutral': neu, 'total': total},
                'overall': overall
            }
            print(f"   📰 {total} articles | +{pos} ={neu} -{neg} → {overall}")
            for n in news[:3]:
                if 'title' in n:
                    emoji = '🟢' if n['sentiment'] == 'positive' else ('🔴' if n['sentiment'] == 'negative' else '🟡')
                    print(f"   {emoji} {n['title'][:60]}")
        else:
            all_sentiment['keywords'][kw] = {'news': news, 'overall': 'unknown'}
            print(f"   ❌ No data or error")
    
    # Economic news
    print(f"\n{'=' * 60}")
    print("宏观经济新闻 — Economic News")
    print("=" * 60)
    
    econ_news = fetch_economic_news()
    all_sentiment['economic_news'] = econ_news
    for n in econ_news[:8]:
        if 'title' in n:
            emoji = '🟢' if n['sentiment'] == 'positive' else ('🔴' if n['sentiment'] == 'negative' else '🟡')
            print(f"   {emoji} {n['title'][:80]}")
    
    # Build summary
    for kw, data in all_sentiment['keywords'].items():
        all_sentiment['summary'][kw] = data.get('overall', 'unknown')
    
    # Save
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_sentiment, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 舆情数据已保存至: {output_path}")


if __name__ == '__main__':
    main()

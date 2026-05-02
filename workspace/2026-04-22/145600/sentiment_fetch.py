#!/usr/bin/env python3
"""
舆情抓取脚本 — 2026-04-22 午间
Keywords: 消费、医疗、军工、科技、光伏、AI、半导体、稀土、黄金、航天、科创、5G、电力、化工、矿业、机器人
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

ENV_PYTHON = '/usr/local/Caskroom/miniforge/base/envs/finance-analysis/bin/python'

try:
    import akshare as ak
except ImportError:
    print("❌ akshare not installed")
    sys.exit(1)

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    if not text or not isinstance(text, str):
        return "neutral"
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '反弹', '上行',
                      '景气', '加速', '超预期', '放量', '拉升', '暴涨', '回暖', '修复', '走强',
                      '利多', '积极', '改善', '获益', '飙升', '新高', '突破']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '下行', '回调', '跌停',
                      '崩盘', '暴雷', '亏损', '走弱', '跳水', '萎缩', '承压', '恶化', '制裁',
                      '打压', '下降', '减持', '破位', '警示']

    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"


def fetch_keyword_news(keyword, max_items=8):
    """Fetch news for a keyword from East Money"""
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is not None and len(news) > 0:
            results = []
            for _, row in news.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                source = str(row.get('文章来源', row.get('source', '')))
                pub_date = str(row.get('发布时间', row.get('date', '')))
                sentiment = simple_sentiment(title + content)
                results.append({
                    'title': title,
                    'source': source,
                    'date': pub_date,
                    'sentiment': sentiment,
                })
            return results
    except Exception as e:
        print(f"  ⚠️ {keyword} 新闻获取失败: {e}")
    return []


def aggregate_sentiment(news_list):
    """Aggregate sentiment from a list of news items"""
    if not news_list:
        return {"overall": "neutral", "positive": 0, "negative": 0, "neutral": 0}
    counts = {"positive": 0, "negative": 0, "neutral": 0}
    for item in news_list:
        s = item.get('sentiment', 'neutral')
        counts[s] = counts.get(s, 0) + 1
    total = sum(counts.values())
    if counts['positive'] > counts['negative'] and counts['positive'] > total * 0.4:
        overall = "positive"
    elif counts['negative'] > counts['positive'] and counts['negative'] > total * 0.4:
        overall = "negative"
    else:
        overall = "neutral"
    return {"overall": overall, **counts}


def main():
    print("=" * 60)
    print("📰 舆情抓取 — 2026-04-22 午间")
    print("=" * 60)

    keywords = [
        'AI', '人工智能', '5G', '算力',
        '消费', '医疗', '医药',
        '军工', '航天', '国防',
        '光伏', '新能源',
        '半导体', '芯片',
        '科创', '科技',
        '黄金', '白银',
        '稀土', '有色',
        '化工', '电力',
        '机器人',
        '中美贸易', '关税',
        '伊朗',
    ]

    all_sentiment = {}
    all_news = {}

    for kw in keywords:
        print(f"\n  → 抓取关键词: {kw}")
        news = fetch_keyword_news(kw, max_items=5)
        if news:
            agg = aggregate_sentiment(news)
            all_sentiment[kw] = agg
            all_news[kw] = news
            print(f"    📊 {kw}: {agg['overall']} (P:{agg['positive']} N:{agg['negative']} U:{agg['neutral']})")
            for item in news[:3]:
                print(f"    📄 [{item['sentiment']}] {item['title'][:60]}")
        else:
            all_sentiment[kw] = {"overall": "no_data", "positive": 0, "negative": 0, "neutral": 0}
            print(f"    ⚠️ 无数据")

    # Fetch economic news from Baidu
    print("\n\n[2] 百度财经新闻...")
    try:
        econ_news = ak.news_economic_baidu()
        if econ_news is not None and len(econ_news) > 0:
            econ_list = []
            for _, row in econ_news.head(10).iterrows():
                title = str(row.get('title', ''))
                content = str(row.get('content', row.get('title', '')))
                sentiment = simple_sentiment(title + content)
                econ_list.append({
                    'title': title,
                    'sentiment': sentiment,
                })
                print(f"  📄 [{sentiment}] {title[:70]}")
            all_news['百度财经'] = econ_list
    except Exception as e:
        print(f"  ⚠️ 百度财经新闻获取失败: {e}")

    # Save results
    output = {
        'date': '2026-04-22',
        'session': 'midday',
        'keyword_sentiment': all_sentiment,
        'keyword_news': all_news,
    }

    out_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n✅ 舆情数据已保存至: {out_path}")
    return output


if __name__ == '__main__':
    main()

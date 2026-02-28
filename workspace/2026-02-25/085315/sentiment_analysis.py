#!/usr/bin/env python3
"""
Sentiment Analysis Script
Date: 2026-02-25
Keywords: 消费、医疗、军工、科技、光伏、AI、半导体、稀土、黄金、航天、科创、机器人、通信、电力、电网、港股、红利、白银、有色、豆粕、化工
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
except ImportError:
    print("akshare not installed")
    sys.exit(1)

SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)
from scripts.utils import make_serializable

keywords = [
    "消费", "医疗", "军工", "科技", "光伏", "AI", "半导体",
    "稀土", "黄金", "航天", "科创", "机器人", "通信", "电力",
    "电网", "港股", "红利", "白银", "有色", "豆粕", "化工"
]

positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '暴涨', '回暖', '提振', '超预期', '加速', '反弹', '走强', '涨停', '火热', '看好', '复苏', '新高', '飙升']
negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '大跌', '跌停', '下行', '回落', '放缓', '走弱', '低迷', '恶化', '抛售', '暴雷', '亏损', '下滑', '崩盘', '缩减']

def simple_sentiment(text):
    if not text:
        return "neutral"
    pos_count = sum(1 for word in positive_words if word in str(text))
    neg_count = sum(1 for word in negative_words if word in str(text))
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

all_sentiment_data = {}

# 1. Fetch economic news from Baidu
print("=== 百度财经新闻 ===")
try:
    econ_news = ak.news_economic_baidu()
    if econ_news is not None and not econ_news.empty:
        top_econ = econ_news.head(15)
        econ_list = []
        for _, row in top_econ.iterrows():
            title = str(row.get('title', row.iloc[0]) if 'title' in row.index else row.iloc[0])
            content = str(row.get('content', title) if 'content' in row.index else title)
            sent = simple_sentiment(title + " " + content)
            econ_list.append({'title': title, 'sentiment': sent})
            print(f"  [{sent}] {title}")
        all_sentiment_data['economic_news'] = econ_list
except Exception as e:
    print(f"  Error: {e}")
    all_sentiment_data['economic_news'] = []

# 2. Keyword-based news search via stock_news_em
print("\n=== 关键词新闻扫描 ===")
keyword_sentiments = {}

for kw in keywords:
    try:
        print(f"\n--- {kw} ---")
        news = ak.stock_news_em(symbol=kw)
        if news is not None and not news.empty:
            top_news = news.head(5)
            kw_data = []
            pos = 0
            neg = 0
            neu = 0
            for _, row in top_news.iterrows():
                # Try different possible column names
                title = ""
                content = ""
                for col in row.index:
                    col_lower = str(col).lower()
                    if '标题' in col_lower or 'title' in col_lower or col == '新闻标题':
                        title = str(row[col])
                    if '内容' in col_lower or 'content' in col_lower or col == '新闻内容':
                        content = str(row[col])

                if not title:
                    title = str(row.iloc[0])
                if not content:
                    content = str(row.iloc[1]) if len(row) > 1 else title

                sent = simple_sentiment(title + " " + content)
                kw_data.append({'title': title[:100], 'sentiment': sent})
                if sent == 'positive':
                    pos += 1
                elif sent == 'negative':
                    neg += 1
                else:
                    neu += 1
                print(f"  [{sent}] {title[:80]}")

            if pos > neg:
                overall = "positive"
            elif neg > pos:
                overall = "negative"
            else:
                overall = "neutral"

            keyword_sentiments[kw] = {
                'overall': overall,
                'positive': pos,
                'negative': neg,
                'neutral': neu,
                'headlines': kw_data
            }
        else:
            keyword_sentiments[kw] = {'overall': 'neutral', 'positive': 0, 'negative': 0, 'neutral': 0, 'headlines': []}
            print(f"  No news found")
    except Exception as e:
        print(f"  Error for {kw}: {e}")
        keyword_sentiments[kw] = {'overall': 'neutral', 'positive': 0, 'negative': 0, 'neutral': 0, 'headlines': [], 'error': str(e)}

all_sentiment_data['keyword_sentiments'] = keyword_sentiments

# Save
clean_data = make_serializable(all_sentiment_data)
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(clean_data, f, indent=4, ensure_ascii=False)

print(f"\n\nSentiment data saved to {output_path}")

# Summary
print("\n=== SENTIMENT SUMMARY ===")
for kw, data in keyword_sentiments.items():
    emoji = "🟢" if data['overall'] == 'positive' else ("🔴" if data['overall'] == 'negative' else "🟡")
    print(f"  {emoji} {kw}: {data['overall']} (pos={data['positive']}, neg={data['negative']}, neu={data['neutral']})")

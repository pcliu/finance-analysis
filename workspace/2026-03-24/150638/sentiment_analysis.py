#!/usr/bin/env python3
"""
Sentiment Analysis Script - 2026-03-24
Scans news for key financial keywords.
"""

import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import akshare as ak

# Simple sentiment function
def simple_sentiment(text):
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '拉升', '涨停', '飙升', '大涨', '暴涨', '反弹', '回升', '走强', '活跃', '加速', '超预期', '景气', '放量', '新高']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停', '大跌', '崩盘', '走低', '回调', '低开', '破位', '承压', '萎缩', '下滑', '低迷', '恐慌', '抛售', '缩量']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

# Keywords to scan
keywords = [
    '消费', '红利', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土',
    '黄金', '航天', '科创', '5G', '通信', '芯片', '机器人', '化工', '有色金属',
    '新能源', '电力', '储能', '算力', '钼', '铜', '白银', '石油', '中东',
    '港股', '恒生科技', '航空', '关税', '特朗普', '国防', '电网', '工程机械',
    '豆粕', '粮食', '矿业'
]

sentiment_data = {}

for keyword in keywords:
    print(f"抓取 '{keyword}' 新闻...")
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is not None and len(news) > 0:
            top_news = news.head(5)
            articles = []
            pos_count = 0
            neg_count = 0
            neu_count = 0
            for _, row in top_news.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', title)))
                sentiment = simple_sentiment(title + ' ' + content)
                if sentiment == 'positive':
                    pos_count += 1
                elif sentiment == 'negative':
                    neg_count += 1
                else:
                    neu_count += 1
                articles.append({
                    'title': title,
                    'sentiment': sentiment
                })
            
            if pos_count > neg_count + 1:
                overall = "强偏多"
            elif pos_count > neg_count:
                overall = "偏多"
            elif neg_count > pos_count + 1:
                overall = "强偏空"
            elif neg_count > pos_count:
                overall = "偏空"
            else:
                overall = "中性"
            
            sentiment_data[keyword] = {
                'overall': overall,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'articles': articles
            }
            print(f"  ✅ {overall} (正{pos_count}/负{neg_count}/中{neu_count})")
        else:
            sentiment_data[keyword] = {'overall': '无数据', 'articles': []}
            print(f"  ⚠️ 无数据")
    except Exception as e:
        sentiment_data[keyword] = {'overall': '获取失败', 'error': str(e), 'articles': []}
        print(f"  ❌ 错误: {e}")

# Also get general economic news
print("\n抓取百度财经新闻...")
try:
    economic_news = ak.news_economic_baidu()
    if economic_news is not None and len(economic_news) > 0:
        top_economic = economic_news.head(10)
        econ_articles = []
        for _, row in top_economic.iterrows():
            title = str(row.get('title', ''))
            econ_articles.append({'title': title})
        sentiment_data['_economic_headlines'] = econ_articles
        print(f"  ✅ 获取 {len(econ_articles)} 条")
except Exception as e:
    print(f"  ❌ 百度财经: {e}")

# CCTV news
print("抓取央视新闻...")
try:
    cctv = ak.news_cctv()
    if cctv is not None and len(cctv) > 0:
        top_cctv = cctv.head(8)
        cctv_articles = []
        for _, row in top_cctv.iterrows():
            title = str(row.get('title', ''))
            cctv_articles.append({'title': title})
        sentiment_data['_cctv_headlines'] = cctv_articles
        print(f"  ✅ 获取 {len(cctv_articles)} 条")
except Exception as e:
    print(f"  ❌ 央视新闻: {e}")

# Save results
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sentiment_data, f, indent=4, ensure_ascii=False)

print(f"\n✅ 舆情分析完成，数据已保存到 {output_path}")

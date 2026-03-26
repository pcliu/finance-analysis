#!/usr/bin/env python3
"""Sentiment Analysis - 2026-03-26"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading')))
from scripts.utils import make_serializable

import akshare as ak
import pandas as pd

# Simple sentiment function
def simple_sentiment(text):
    if not isinstance(text, str):
        return "neutral"
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '反弹', '走强', '涨停', '暴涨', '飙升', '拉升', '领涨', '活跃', '放量', '提振', '加速', '扩产', '景气', '超预期', '新高', '回暖', '复苏', '丰收']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '跌停', '大跌', '走弱', '重挫', '崩盘', '下滑', '萎缩', '低迷', '减持', '亏损', '回调', '缩量', '溢价风险', '跌幅', '承压', '下行']

    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)

    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

# Keywords to scan
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体', '稀土', '黄金', '航天',
    '科创', '红利', '5G', '新能源', '芯片', '算力', '机器人', '储能', '电力',
    '电网', '化工', '矿业', '有色金属', '白银', '钼', '铜', '豆粕', '粮食',
    '港股', '恒生科技', '中东', '伊朗', '石油', '工程机械', '航空', '通信',
    '关税', '特朗普', '国防'
]

all_sentiment = {}

for kw in KEYWORDS:
    print(f"\n--- Scanning: {kw} ---")
    try:
        news = ak.stock_news_em(symbol=kw)
        if news is not None and len(news) > 0:
            top_news = news.head(5)
            sentiments = []
            for _, row in top_news.iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', title)))
                sent = simple_sentiment(title + ' ' + content)
                sentiments.append({
                    'title': title,
                    'sentiment': sent,
                    'source': str(row.get('文章来源', row.get('source', ''))),
                    'time': str(row.get('发布时间', row.get('publish_time', '')))
                })
                print(f"  [{sent}] {title[:60]}")
            
            pos = sum(1 for s in sentiments if s['sentiment'] == 'positive')
            neg = sum(1 for s in sentiments if s['sentiment'] == 'negative')
            neu = sum(1 for s in sentiments if s['sentiment'] == 'neutral')
            
            if pos > neg:
                overall = '强偏多' if pos >= 3 else '偏多'
            elif neg > pos:
                overall = '强偏空' if neg >= 3 else '偏空'
            else:
                overall = '中性'
            
            all_sentiment[kw] = {
                'overall': overall,
                'positive': pos,
                'negative': neg,
                'neutral': neu,
                'news': sentiments
            }
            print(f"  Overall: {overall} (P:{pos}/Neg:{neg}/Neu:{neu})")
        else:
            print(f"  No news found")
            all_sentiment[kw] = {'overall': '无数据', 'positive': 0, 'negative': 0, 'neutral': 0, 'news': []}
    except Exception as e:
        print(f"  Error: {e}")
        all_sentiment[kw] = {'overall': 'error', 'error': str(e)}

# Also fetch general economic news
print("\n--- General Economic News (Baidu) ---")
try:
    econ_news = ak.news_economic_baidu()
    if econ_news is not None and len(econ_news) > 0:
        general = []
        for _, row in econ_news.head(10).iterrows():
            title = str(row.get('title', ''))
            general.append({
                'title': title,
                'sentiment': simple_sentiment(title),
                'time': str(row.get('date', ''))
            })
            print(f"  {title[:80]}")
        all_sentiment['_general_economic'] = general
except Exception as e:
    print(f"  Baidu economic news error: {e}")

# CCTV News
print("\n--- CCTV News ---")
try:
    cctv = ak.news_cctv(date="20260326")
    if cctv is not None and len(cctv) > 0:
        cctv_items = []
        for _, row in cctv.head(10).iterrows():
            title = str(row.get('title', ''))
            cctv_items.append({'title': title})
            print(f"  {title[:80]}")
        all_sentiment['_cctv_news'] = cctv_items
except Exception as e:
    print(f"  CCTV news error: {e}")

# Save
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(make_serializable(all_sentiment), f, indent=2, ensure_ascii=False)
print(f"\nSentiment data saved to {output_path}")
print("Done!")

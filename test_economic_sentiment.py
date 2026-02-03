#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test updated economic-sentiment skill with correct API
"""

import akshare as ak

print("Testing Economic Sentiment Skill (Updated)...")
print("=" * 50)

# Test 1: Get stock news
print("\n1. 获取股票新闻（东方财富）...")
try:
    news = ak.stock_news_em(symbol="芯片")
    print(f"✅ 成功获取 {len(news)} 条新闻")
    if len(news) > 0:
        print(f"   最新一条: {news.iloc[0]['新闻标题']}")
except Exception as e:
    print(f"❌ 失败: {e}")

# Test 2: Get economic news from Baidu
print("\n2. 获取百度财经新闻...")
try:
    econ_news = ak.news_economic_baidu()
    print(f"✅ 成功获取 {len(econ_news)} 条新闻")
    if len(econ_news) > 0:
        print(f"   最新一条: {econ_news.iloc[0].get('标题', 'N/A')}")
except Exception as e:
    print(f"❌ 失败: {e}")

# Test 3: Get CCTV news
print("\n3. 获取央视新闻...")
try:
    cctv = ak.news_cctv()
    print(f"✅ 成功获取 {len(cctv)} 条新闻")
    if len(cctv) > 0:
        print(f"   最新一条: {cctv.iloc[0].get('title', 'N/A')}")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "=" * 50)
print("✅ Economic Sentiment Skill 测试完成！")

#!/usr/bin/env python3
"""
舆情分析脚本
日期: 2026-02-06
使用AkShare获取市场新闻和舆情
"""

import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 定义关键词列表和简单情绪分析函数
KEYWORDS = ["消费", "医疗", "军工", "科技", "光伏", "AI", "半导体", "稀土", "黄金", "航天", "科创"]

def simple_sentiment(text):
    """简单的关键词情绪打分"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '反弹', '回暖', '攀升', '走高', '暴涨', '领涨']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回落', '下挫', '跳水', '崩盘', '承压', '走低']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def get_news_with_akshare():
    """使用AkShare获取财经新闻"""
    try:
        import akshare as ak
        
        results = {
            "baidu_news": [],
            "stock_news": {},
            "cctv_news": [],
            "keyword_sentiment": {}
        }
        
        # 1. 获取百度财经新闻
        print("获取百度财经新闻...")
        try:
            baidu_news = ak.news_economic_baidu()
            if baidu_news is not None and not baidu_news.empty:
                for i, row in baidu_news.head(10).iterrows():
                    title = row.get('title', '') or row.get('标题', '')
                    if title:
                        results["baidu_news"].append({
                            "title": title,
                            "sentiment": simple_sentiment(title)
                        })
                print(f"  ✓ 获取{len(results['baidu_news'])}条百度财经新闻")
        except Exception as e:
            print(f"  ✗ 百度财经新闻获取失败: {e}")
        
        # 2. 获取关键词相关新闻
        print("\n获取关键词相关新闻...")
        for keyword in KEYWORDS:
            try:
                news_df = ak.stock_news_em(symbol=keyword)
                if news_df is not None and not news_df.empty:
                    news_list = []
                    sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
                    
                    for i, row in news_df.head(5).iterrows():
                        title = str(row.get('新闻标题', ''))
                        content = str(row.get('新闻内容', ''))
                        full_text = title + content
                        sentiment = simple_sentiment(full_text)
                        sentiment_counts[sentiment] += 1
                        
                        news_list.append({
                            "title": title[:80],
                            "sentiment": sentiment
                        })
                    
                    results["stock_news"][keyword] = news_list
                    
                    # 计算整体情绪
                    pos = sentiment_counts["positive"]
                    neg = sentiment_counts["negative"]
                    if pos > neg:
                        overall = "偏多"
                    elif neg > pos:
                        overall = "偏空"
                    else:
                        overall = "中性"
                    
                    results["keyword_sentiment"][keyword] = {
                        "positive": pos,
                        "negative": neg,
                        "neutral": sentiment_counts["neutral"],
                        "overall": overall
                    }
                    
                    print(f"  ✓ {keyword}: {pos}正/{neg}负/{sentiment_counts['neutral']}中 → {overall}")
            except Exception as e:
                print(f"  ✗ {keyword}: 获取失败 - {str(e)[:50]}")
                results["keyword_sentiment"][keyword] = {
                    "positive": 0, "negative": 0, "neutral": 0, "overall": "无数据"
                }
        
        # 3. 获取央视新闻
        print("\n获取央视新闻...")
        try:
            cctv_news = ak.news_cctv()
            if cctv_news is not None and not cctv_news.empty:
                for i, row in cctv_news.head(5).iterrows():
                    title = row.get('title', '') or row.get('标题', '')
                    if title:
                        results["cctv_news"].append({
                            "title": title,
                            "sentiment": simple_sentiment(title)
                        })
                print(f"  ✓ 获取{len(results['cctv_news'])}条央视新闻")
        except Exception as e:
            print(f"  ✗ 央视新闻获取失败: {e}")
        
        return results
        
    except ImportError:
        print("AkShare未安装，跳过舆情获取")
        return {"error": "AkShare not installed"}
    except Exception as e:
        print(f"舆情获取失败: {e}")
        return {"error": str(e)}


def main():
    print("=" * 60)
    print(f"舆情分析 - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    results = get_news_with_akshare()
    
    # 保存结果
    output_file = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n舆情数据已保存: {output_file}")
    
    # 生成摘要
    print("\n" + "=" * 60)
    print("舆情摘要")
    print("=" * 60)
    
    if "keyword_sentiment" in results:
        for kw, data in results["keyword_sentiment"].items():
            if data.get("overall") != "无数据":
                emoji = "🟢" if data["overall"] == "偏多" else ("🔴" if data["overall"] == "偏空" else "⚪")
                print(f"  {emoji} {kw}: {data['overall']} ({data['positive']}/{data['negative']}/{data['neutral']})")
    
    return results


if __name__ == "__main__":
    main()

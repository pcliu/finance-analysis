#!/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
# -*- coding: utf-8 -*-
"""
Economic Sentiment Analysis - 2026-02-03
市场舆情分析 - 2月2-3日
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import json

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    if pd.isna(text):
        return "neutral"
    
    text = str(text)
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '反弹', '回暖', '企稳', '看好']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回调', '承压', '下行', '担忧']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def analyze_sentiment():
    """收集并分析市场舆情"""
    
    print("="*80)
    print("市场舆情分析 - Market Sentiment Analysis")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {
        'timestamp': datetime.now().isoformat(),
        'news_summary': [],
        'hot_topics': [],
        'sentiment_overview': {}
    }
    
    # 1. 获取经济新闻（百度财经）
    print("\n📰 [1/5] 获取百度财经新闻...")
    try:
        economic_news = ak.news_economic_baidu()
        if economic_news is not None and len(economic_news) > 0:
            print(f"✅ 成功获取 {len(economic_news)} 条经济新闻")
            
            # 分析最新10条
            latest_economic = economic_news.head(10)
            for idx, row in latest_economic.iterrows():
                title = row.get('title', row.get('标题', ''))
                content = row.get('content', row.get('内容', ''))
                pub_time = row.get('publish_time', row.get('发布时间', ''))
                
                sentiment = simple_sentiment(str(title) + str(content))
                results['news_summary'].append({
                    'source': '百度财经',
                    'title': title,
                    'time': str(pub_time),
                    'sentiment': sentiment
                })
            
            print(f"   最新标题: {latest_economic.iloc[0].get('title', latest_economic.iloc[0].get('标题', 'N/A'))}")
    except Exception as e:
        print(f"⚠️ 百度财经新闻获取失败: {str(e)}")
    
    # 2. 获取央视新闻
    print("\n📺 [2/5] 获取央视新闻...")
    try:
        cctv_news = ak.news_cctv()
        if cctv_news is not None and len(cctv_news) > 0:
            print(f"✅ 成功获取 {len(cctv_news)} 条央视新闻")
            
            latest_cctv = cctv_news.head(5)
            for idx, row in latest_cctv.iterrows():
                title = row.get('title', row.get('标题', ''))
                content = row.get('content', row.get('内容', ''))
                pub_time = row.get('time', row.get('时间', ''))
                
                sentiment = simple_sentiment(str(title) + str(content))
                results['news_summary'].append({
                    'source': '央视新闻',
                    'title': title,
                    'time': str(pub_time),
                    'sentiment': sentiment
                })
            
            print(f"   最新标题: {latest_cctv.iloc[0].get('title', latest_cctv.iloc[0].get('标题', 'N/A'))}")
    except Exception as e:
        print(f"⚠️ 央视新闻获取失败: {str(e)}")
    
    # 3. 获取关键行业新闻
    print("\n🏭 [3/5] 获取行业新闻...")
    keywords = ['消费', '军工', '医疗', '芯片', '新能源', '黄金', '白银']
    
    for keyword in keywords:
        try:
            industry_news = ak.stock_news_em(symbol=keyword)
            if industry_news is not None and len(industry_news) > 0:
                print(f"   {keyword}: {len(industry_news)} 条新闻")
                
                # 只取最新3条
                latest = industry_news.head(3)
                for idx, row in latest.iterrows():
                    title = row.get('新闻标题', row.get('title', ''))
                    content = row.get('新闻内容', row.get('content', ''))
                    pub_time = row.get('发布时间', row.get('time', ''))
                    
                    sentiment = simple_sentiment(str(title) + str(content))
                    results['hot_topics'].append({
                        'keyword': keyword,
                        'title': title,
                        'time': str(pub_time),
                        'sentiment': sentiment
                    })
        except Exception as e:
            print(f"   {keyword}: 获取失败 - {str(e)}")
    
    # 4. 统计情绪分布
    print("\n📊 [4/5] 统计情绪分布...")
    all_sentiments = [item['sentiment'] for item in results['news_summary']] + \
                     [item['sentiment'] for item in results['hot_topics']]
    
    sentiment_counts = pd.Series(all_sentiments).value_counts()
    total = len(all_sentiments)
    
    results['sentiment_overview'] = {
        'positive': int(sentiment_counts.get('positive', 0)),
        'negative': int(sentiment_counts.get('negative', 0)),
        'neutral': int(sentiment_counts.get('neutral', 0)),
        'total': total,
        'positive_pct': round(sentiment_counts.get('positive', 0) / total * 100, 1) if total > 0 else 0,
        'negative_pct': round(sentiment_counts.get('negative', 0) / total * 100, 1) if total > 0 else 0,
        'neutral_pct': round(sentiment_counts.get('neutral', 0) / total * 100, 1) if total > 0 else 0
    }
    
    print(f"   积极: {results['sentiment_overview']['positive']} ({results['sentiment_overview']['positive_pct']}%)")
    print(f"   消极: {results['sentiment_overview']['negative']} ({results['sentiment_overview']['negative_pct']}%)")
    print(f"   中性: {results['sentiment_overview']['neutral']} ({results['sentiment_overview']['neutral_pct']}%)")
    
    # 5. 保存结果
    print("\n💾 [5/5] 保存分析结果...")
    output_file = 'sentiment_analysis_data.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 数据已保存至: {output_file}")
    
    print("\n" + "="*80)
    print("✅ 舆情分析完成！")
    print("="*80)
    
    return results

if __name__ == "__main__":
    analyze_sentiment()

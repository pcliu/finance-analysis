#!/usr/bin/env python3
"""
舆情分析脚本
生成时间: 2026-02-05
"""
import json
import os
from datetime import datetime

try:
    import akshare as ak
except ImportError:
    print("警告: akshare未安装")
    ak = None

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 关键词列表
KEYWORDS = [
    "消费", "医疗", "军工", "科技", "光伏", "AI", 
    "半导体", "稀土", "黄金", "航天", "科创",
    "芯片", "机器人", "新能源", "港股"
]

def simple_sentiment(text):
    """简单情绪分析"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '反弹', '走高', '大涨', '加速', '回暖', '复苏']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回落', '走低', '承压', '调整', '下挫', '抛售']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def fetch_news():
    """获取新闻"""
    results = {
        'generated_at': datetime.now().isoformat(),
        'stock_news': [],
        'economic_news': [],
        'sentiment_summary': {}
    }
    
    if ak is None:
        print("akshare未安装，跳过新闻获取")
        return results
    
    # 获取经济新闻
    try:
        print("获取百度财经新闻...")
        economic_news = ak.news_economic_baidu()
        for idx, row in economic_news.head(15).iterrows():
            news_item = {
                'title': row.get('title', ''),
                'content': row.get('content', str(row)),
                'sentiment': simple_sentiment(str(row))
            }
            results['economic_news'].append(news_item)
            print(f"  [{news_item['sentiment']}] {news_item['title'][:50]}")
    except Exception as e:
        print(f"获取经济新闻失败: {e}")
    
    # 获取关键词相关新闻
    for keyword in KEYWORDS[:8]:  # 限制关键词数量
        try:
            print(f"\n搜索 '{keyword}' 相关新闻...")
            news = ak.stock_news_em(symbol=keyword)
            keyword_sentiment = {'positive': 0, 'negative': 0, 'neutral': 0}
            
            for idx, row in news.head(5).iterrows():
                title = row.get('新闻标题', '')
                content = row.get('新闻内容', str(row))
                full_text = title + " " + content
                sentiment = simple_sentiment(full_text)
                keyword_sentiment[sentiment] += 1
                
                results['stock_news'].append({
                    'keyword': keyword,
                    'title': title,
                    'sentiment': sentiment
                })
                print(f"  [{sentiment}] {title[:40]}...")
            
            # 计算该关键词整体情绪
            total = sum(keyword_sentiment.values())
            if total > 0:
                if keyword_sentiment['positive'] > keyword_sentiment['negative']:
                    overall = 'positive'
                elif keyword_sentiment['negative'] > keyword_sentiment['positive']:
                    overall = 'negative'
                else:
                    overall = 'neutral'
                results['sentiment_summary'][keyword] = {
                    'overall': overall,
                    'positive': keyword_sentiment['positive'],
                    'negative': keyword_sentiment['negative'],
                    'neutral': keyword_sentiment['neutral']
                }
        except Exception as e:
            print(f"  获取 '{keyword}' 新闻失败: {e}")
    
    return results

def main():
    print("=" * 60)
    print("舆情分析")
    print(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = fetch_news()
    
    # 保存结果
    output_file = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n舆情数据已保存至: {output_file}")
    
    # 打印情绪汇总
    print("\n" + "=" * 60)
    print("情绪汇总")
    print("=" * 60)
    for keyword, sentiment in results.get('sentiment_summary', {}).items():
        print(f"{keyword}: {sentiment['overall']} (正面{sentiment['positive']}/负面{sentiment['negative']}/中性{sentiment['neutral']})")
    
    return results

if __name__ == "__main__":
    main()

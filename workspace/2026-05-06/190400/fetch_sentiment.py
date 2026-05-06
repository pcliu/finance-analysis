import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/economic-sentiment')))

import akshare as ak

def simple_sentiment(text):
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '大涨', '牛市', '复苏', '红利', '提振', '看好']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '大跌', '熊市', '衰退', '抛售', '看空']
    
    pos_count = sum(1 for word in positive_words if word in str(text))
    neg_count = sum(1 for word in negative_words if word in str(text))
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

def fetch_sentiment():
    keywords = ["消费", "医疗", "军工", "科技", "光伏", "AI", "半导体", "稀土", "黄金", "航天", "科创"]
    results = {}
    
    for kw in keywords:
        print(f"Fetching news for {kw}...")
        try:
            news = ak.stock_news_em(symbol=kw)
            news_items = []
            sentiment_score = 0
            
            for item in news.head(5).itertuples():
                sentiment = simple_sentiment(item.新闻内容)
                news_items.append({
                    "title": item.新闻标题,
                    "sentiment": sentiment
                })
                if sentiment == 'positive':
                    sentiment_score += 1
                elif sentiment == 'negative':
                    sentiment_score -= 1
            
            overall_sentiment = "neutral"
            if sentiment_score > 0:
                overall_sentiment = "positive"
            elif sentiment_score < 0:
                overall_sentiment = "negative"
                
            results[kw] = {
                "overall": overall_sentiment,
                "news": news_items
            }
        except Exception as e:
            results[kw] = {"error": str(e)}
            
    with open(os.path.join(SCRIPT_DIR, 'sentiment_data.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
        
    print("Sentiment analysis complete.")

if __name__ == '__main__':
    fetch_sentiment()

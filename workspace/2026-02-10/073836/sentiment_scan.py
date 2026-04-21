#!/usr/bin/env python3
"""
舆情扫描脚本 - 2026-02-10
扫描消费、医疗、军工、科技、光伏、AI、半导体、稀土、黄金、航天、科创等关键词
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
    print("✅ AkShare 已加载")
except ImportError:
    print("❌ 无法导入 AkShare")
    sys.exit(1)

# 关键词列表
keywords = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '机器人', '5G', '通信',
    '红利', '电网', '化工', '新能源', '港股', 'DeepSeek'
]

positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '回升', '反弹', '复苏', '加速', '超预期', '放量', '领涨', '大涨', '暴涨', '走强', '提振', '乐观', '积极']
negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回调', '下行', '承压', '走弱', '缩水', '破位', '低迷', '萎缩', '减持', '亏损', '恐慌', '暴雷']

def simple_sentiment(text):
    """简单情绪打分"""
    if not text:
        return 'neutral'
    pos = sum(1 for w in positive_words if w in str(text))
    neg = sum(1 for w in negative_words if w in str(text))
    if pos > neg:
        return 'positive'
    elif neg > pos:
        return 'negative'
    return 'neutral'

def fetch_news_for_keyword(keyword, max_items=8):
    """抓取关键词新闻"""
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is not None and not news.empty:
            items = []
            for _, row in news.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', '')))
                source = str(row.get('文章来源', row.get('source', '')))
                pub_time = str(row.get('发布时间', row.get('publish_time', '')))
                sentiment = simple_sentiment(title + ' ' + content)
                items.append({
                    'title': title,
                    'sentiment': sentiment,
                    'source': source,
                    'time': pub_time,
                })
            return items
    except Exception as e:
        print(f"  ⚠️  获取 '{keyword}' 新闻失败: {e}")
    return []

def fetch_economic_news():
    """获取宏观经济新闻"""
    try:
        news = ak.news_economic_baidu()
        if news is not None and not news.empty:
            items = []
            for _, row in news.head(10).iterrows():
                title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
                content = str(row.get('content', ''))
                sentiment = simple_sentiment(title + ' ' + content)
                items.append({
                    'title': title,
                    'sentiment': sentiment,
                })
            return items
    except Exception as e:
        print(f"  ⚠️  获取百度财经新闻失败: {e}")
    return []

def main():
    print("=" * 60)
    print("舆情扫描 - 2026-02-10")
    print("=" * 60)
    
    all_sentiment = {}
    
    # 1. 关键词新闻扫描
    print("\n📰 关键词新闻扫描...")
    for kw in keywords:
        print(f"\n  🔍 扫描关键词: {kw}")
        items = fetch_news_for_keyword(kw, max_items=5)
        if items:
            pos_count = sum(1 for i in items if i['sentiment'] == 'positive')
            neg_count = sum(1 for i in items if i['sentiment'] == 'negative')
            neu_count = sum(1 for i in items if i['sentiment'] == 'neutral')
            
            if pos_count > neg_count:
                overall = 'positive'
            elif neg_count > pos_count:
                overall = 'negative'
            else:
                overall = 'neutral'
            
            all_sentiment[kw] = {
                'overall': overall,
                'positive': pos_count,
                'negative': neg_count,
                'neutral': neu_count,
                'total': len(items),
                'headlines': [i['title'] for i in items[:3]],
                'details': items,
            }
            print(f"    → 情绪: {overall} (正面{pos_count}/负面{neg_count}/中性{neu_count})")
            for i in items[:2]:
                print(f"    📌 {i['title'][:60]}... [{i['sentiment']}]")
        else:
            all_sentiment[kw] = {
                'overall': 'no_data',
                'positive': 0,
                'negative': 0,
                'neutral': 0,
                'total': 0,
                'headlines': [],
                'details': [],
            }
            print(f"    → 无数据")
    
    # 2. 百度财经新闻
    print("\n📊 百度财经宏观新闻...")
    economic_news = fetch_economic_news()
    
    all_sentiment['_macro_economic'] = {
        'overall': 'neutral',
        'headlines': [i['title'] for i in economic_news[:5]],
        'details': economic_news,
    }
    
    if economic_news:
        for item in economic_news[:5]:
            print(f"  📌 {item['title'][:70]} [{item['sentiment']}]")
    
    # 保存结果
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_sentiment, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 舆情数据已保存至: {output_path}")
    
    # 打印情绪概览
    print("\n" + "=" * 60)
    print("📊 情绪概览")
    print("-" * 60)
    for kw, data in all_sentiment.items():
        if kw.startswith('_'):
            continue
        emoji = {'positive': '🟢', 'negative': '🔴', 'neutral': '⚪', 'no_data': '❓'}.get(data['overall'], '⚪')
        print(f"  {emoji} {kw:<10} → {data['overall']:<10} (正{data['positive']}/负{data['negative']}/中{data['neutral']})")
    print("=" * 60)

if __name__ == '__main__':
    main()

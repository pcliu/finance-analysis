#!/usr/bin/env python3
"""
舆情分析脚本
日期: 2026-02-24 (盘前分析)
关键词: 消费、医疗、军工、科技、光伏、AI、半导体、稀土、黄金、航天、科创、通信、机器人、港股、红利
"""
import sys
import os
import json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
except ImportError:
    print("akshare 未安装，请安装后重试")
    sys.exit(1)

# 关键词列表
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '通信', '机器人', '港股', '红利',
    '白银', '有色', '豆粕', '电力', '电网'
]

def simple_sentiment(text):
    """简单关键词情绪判断"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '反弹', '飙升',
                      '加速', '扩张', '景气', '回暖', '超预期', '大涨', '拉升', '放量',
                      '资金流入', '看好', '布局', '机遇', '复苏', '提振']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '回调', '跳水',
                      '缩量', '收缩', '低迷', '不及预期', '大跌', '杀跌', '恐慌',
                      '资金流出', '减持', '抛售', '下行', '承压', '萎缩']
    
    pos_count = sum(1 for word in positive_words if word in str(text))
    neg_count = sum(1 for word in negative_words if word in str(text))
    
    if pos_count > neg_count:
        return 'positive'
    elif neg_count > pos_count:
        return 'negative'
    else:
        return 'neutral'

def fetch_news_for_keyword(keyword, max_items=5):
    """抓取某个关键词的新闻"""
    results = []
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is not None and len(news) > 0:
            for i, row in news.head(max_items).iterrows():
                title = str(row.get('新闻标题', row.get('title', '')))
                content = str(row.get('新闻内容', row.get('content', title)))
                pub_time = str(row.get('发布时间', row.get('datetime', '')))
                sentiment = simple_sentiment(title + content)
                results.append({
                    'title': title,
                    'time': pub_time,
                    'sentiment': sentiment,
                    'source': '东方财富'
                })
    except Exception as e:
        print(f"  ⚠️ 抓取 '{keyword}' 新闻失败: {e}")
    return results

def main():
    print(f"开始舆情扫描，共 {len(KEYWORDS)} 个关键词...")
    
    all_sentiment = {}
    
    for kw in KEYWORDS:
        print(f"  扫描 '{kw}'...")
        news = fetch_news_for_keyword(kw, max_items=5)
        
        pos_count = sum(1 for n in news if n['sentiment'] == 'positive')
        neg_count = sum(1 for n in news if n['sentiment'] == 'negative')
        neu_count = sum(1 for n in news if n['sentiment'] == 'neutral')
        
        if pos_count > neg_count:
            overall = 'positive'
        elif neg_count > pos_count:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        all_sentiment[kw] = {
            'keyword': kw,
            'overall': overall,
            'positive_count': pos_count,
            'negative_count': neg_count,
            'neutral_count': neu_count,
            'total': len(news),
            'news': news,
            'top_titles': [n['title'] for n in news[:3]]
        }
        
        emoji = '🟢' if overall == 'positive' else ('🔴' if overall == 'negative' else '🟡')
        print(f"    {emoji} {overall} ({pos_count}+/{neg_count}-/{neu_count}○) - 共{len(news)}条")
    
    # 补充: 百度财经新闻
    baidu_news = []
    try:
        print("\n  获取百度财经新闻...")
        econ_news = ak.news_economic_baidu()
        if econ_news is not None and len(econ_news) > 0:
            for i, row in econ_news.head(10).iterrows():
                title = str(row.get('title', ''))
                baidu_news.append({
                    'title': title,
                    'sentiment': simple_sentiment(title)
                })
            print(f"    ✅ 获取 {len(baidu_news)} 条宏观新闻")
    except Exception as e:
        print(f"    ⚠️ 百度财经新闻获取失败: {e}")
    
    # 补充: 央视新闻
    cctv_news = []
    try:
        print("  获取央视新闻...")
        cctv = ak.news_cctv(date="20260223")
        if cctv is not None and len(cctv) > 0:
            for i, row in cctv.head(5).iterrows():
                title = str(row.get('title', ''))
                cctv_news.append({
                    'title': title,
                    'sentiment': simple_sentiment(title)
                })
            print(f"    ✅ 获取 {len(cctv_news)} 条央视新闻")
    except Exception as e:
        print(f"    ⚠️ 央视新闻获取失败: {e}")
    
    output = {
        'analysis_date': '2026-02-24',
        'keywords': all_sentiment,
        'macro_news_baidu': baidu_news,
        'cctv_news': cctv_news,
    }
    
    output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 舆情分析完成，数据已保存到: {output_path}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
舆情快速扫描 - 2026-02-27
使用 akshare 获取市场新闻和热点
"""
import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
    import pandas as pd
except ImportError:
    print("Missing akshare or pandas, installing...")
    os.system(f"{sys.executable} -m pip install akshare pandas -q")
    import akshare as ak
    import pandas as pd

# 关键词列表
KEYWORDS = [
    '消费', '红利', '医疗', '军工', '航天', '恒生科技', '港股',
    '5G', '通信', '6G', 'AI', '人工智能', '光伏', '科创',
    '半导体', '稀土', '化工', '电力', '电网', '机器人',
    '黄金', '白银', '有色', '矿业', '豆粕', '卫星', '航空',
    '两会', '政策'
]

POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '暴涨', '大涨',
                  '走强', '爆发', '拉升', '涨停', '火爆', '飙升', '提振', '加速',
                  '反弹', '回暖', '景气', '扩张', '扩大', '放量', '催化']
NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '走弱', '承压',
                  '回调', '下滑', '萎缩', '减少', '亏损', '熊市', '暴雷', '制裁',
                  '限制', '收紧', '下降', '跌停', '缩量']

def simple_sentiment(text):
    if not isinstance(text, str):
        return 'neutral', 0, 0
    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    if pos > neg:
        return 'positive', pos, neg
    elif neg > pos:
        return 'negative', pos, neg
    return 'neutral', pos, neg

def fetch_news():
    """获取多源新闻"""
    all_news = []
    
    # 1. 东方财富财经新闻
    try:
        for kw in ['A股', '基金', 'ETF']:
            news = ak.stock_news_em(symbol=kw)
            if news is not None and len(news) > 0:
                for _, row in news.head(15).iterrows():
                    title = str(row.get('新闻标题', row.get('title', '')))
                    content = str(row.get('新闻内容', row.get('content', title)))
                    all_news.append({
                        'source': '东方财富',
                        'title': title,
                        'content': content[:200],
                    })
        print(f"  东方财富: {len(all_news)} 条")
    except Exception as e:
        print(f"  东方财富失败: {e}")
    
    # 2. 百度财经新闻
    try:
        econ_news = ak.news_economic_baidu()
        if econ_news is not None and len(econ_news) > 0:
            count = 0
            for _, row in econ_news.head(15).iterrows():
                title = str(row.get('title', ''))
                content = str(row.get('content', title))
                all_news.append({
                    'source': '百度财经',
                    'title': title,
                    'content': content[:200],
                })
                count += 1
            print(f"  百度财经: {count} 条")
    except Exception as e:
        print(f"  百度财经失败: {e}")
    
    # 3. CCTV新闻
    try:
        cctv = ak.news_cctv(date="20260226")
        if cctv is not None and len(cctv) > 0:
            count = 0
            for _, row in cctv.head(10).iterrows():
                title = str(row.get('title', ''))
                content = str(row.get('content', title))
                all_news.append({
                    'source': 'CCTV',
                    'title': title,
                    'content': content[:200],
                })
                count += 1
            print(f"  CCTV: {count} 条")
    except Exception as e:
        print(f"  CCTV失败: {e}")
    
    return all_news

def analyze_keywords(news_list):
    """按关键词分析情绪"""
    keyword_results = {}
    
    for kw in KEYWORDS:
        matches = []
        for news in news_list:
            text = news['title'] + ' ' + news['content']
            if kw.lower() in text.lower():
                sent, pos_c, neg_c = simple_sentiment(text)
                matches.append({
                    'title': news['title'][:80],
                    'source': news['source'],
                    'sentiment': sent,
                })
        
        if matches:
            pos = sum(1 for m in matches if m['sentiment'] == 'positive')
            neg = sum(1 for m in matches if m['sentiment'] == 'negative')
            neu = sum(1 for m in matches if m['sentiment'] == 'neutral')
            
            if pos > neg * 2:
                overall = '强势偏多'
            elif pos > neg:
                overall = '偏多'
            elif neg > pos * 2:
                overall = '强势偏空'
            elif neg > pos:
                overall = '偏空'
            else:
                overall = '中性'
            
            keyword_results[kw] = {
                'total': len(matches),
                'positive': pos,
                'negative': neg,
                'neutral': neu,
                'overall': overall,
                'top_titles': [m['title'] for m in matches[:5]],
            }
    
    return keyword_results

# ========== 主执行 ==========
print("=" * 60)
print("舆情快速扫描 - 2026-02-27")
print("=" * 60)

print("\n📰 获取新闻数据...")
news_list = fetch_news()
print(f"共获取 {len(news_list)} 条新闻\n")

print("🔍 关键词情绪分析...")
keyword_results = analyze_keywords(news_list)

# 排序输出
sorted_kw = sorted(keyword_results.items(), key=lambda x: x[1]['positive'], reverse=True)

print(f"\n{'关键词':<10} {'总数':>4} {'正面':>4} {'负面':>4} {'中性':>4} {'整体情绪':<10}")
print("-" * 50)
for kw, data in sorted_kw:
    emoji = '🟢' if '偏多' in data['overall'] else ('🔴' if '偏空' in data['overall'] else '🟡')
    print(f"{emoji} {kw:<8} {data['total']:>4} {data['positive']:>4} {data['negative']:>4} {data['neutral']:>4} {data['overall']:<10}")

# 重要新闻标题
print("\n📋 重要新闻标题 (含情绪词):")
important_news = []
for news in news_list:
    text = news['title'] + ' ' + news['content']
    sent, pos_c, neg_c = simple_sentiment(text)
    if pos_c + neg_c >= 1:
        important_news.append({
            'title': news['title'][:80],
            'source': news['source'],
            'sentiment': sent,
            'score': pos_c - neg_c,
        })

important_news.sort(key=lambda x: abs(x['score']), reverse=True)
for i, news in enumerate(important_news[:20], 1):
    emoji = '🟢' if news['sentiment'] == 'positive' else ('🔴' if news['sentiment'] == 'negative' else '🟡')
    print(f"  {i}. {emoji} {news['title']} [{news['source']}]")

# 保存数据
sentiment_data = {
    'date': '2026-02-27',
    'total_news': len(news_list),
    'keyword_analysis': keyword_results,
    'important_news': important_news[:30],
}

output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sentiment_data, f, indent=4, ensure_ascii=False)

print(f"\n✅ 舆情数据已保存至: {output_path}")

#!/usr/bin/env python3
"""
舆情分析脚本 - 2026-03-04
抓取消费、医疗、军工、科技、光伏、AI、半导体、稀土、黄金、航天、科创、通信、机器人等关键词的市场情绪
"""
import sys
import os
import json
import warnings
import time
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

try:
    import akshare as ak
except ImportError:
    print("❌ akshare not installed. Run: pip install akshare")
    sys.exit(1)

# 关键词列表
KEYWORDS = [
    '消费', '医疗', '军工', '科技', '光伏', 'AI', '半导体',
    '稀土', '黄金', '航天', '科创', '通信', '5G', '机器人',
    '电力', '电网', '新能源', '港股', '恒生科技', '红利',
    '化工', '有色金属', '白银', '两会', '国防', '卫星',
    '豆粕', '矿业', '芯片', '算力'
]

# 正面/负面关键词（用于简单情绪判断）
POSITIVE_WORDS = ['上涨', '突破', '利好', '增长', '创新高', '强势', '看好',
                  '回升', '走强', '大涨', '飙升', '加速', '景气', '扩张',
                  '复苏', '反弹', '金叉', '放量', '突围', '爆发', '暴涨',
                  '新高', '跑赢', '超预期', '催化', '提振']
NEGATIVE_WORDS = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '减持',
                  '走弱', '大跌', '熊市', '下行', '萎缩', '衰退', '回调',
                  '破位', '跌停', '缩量', '抛售', '恐慌', '危机', '暴雷',
                  '亏损', '不及预期', '承压']

def simple_sentiment(text):
    """简单关键词情绪评分"""
    if not text:
        return 'neutral', 0, 0
    pos = sum(1 for w in POSITIVE_WORDS if w in str(text))
    neg = sum(1 for w in NEGATIVE_WORDS if w in str(text))
    if pos > neg:
        return 'positive', pos, neg
    elif neg > pos:
        return 'negative', pos, neg
    else:
        return 'neutral', pos, neg

def fetch_keyword_news(keyword, max_items=8):
    """获取某个关键词的新闻"""
    try:
        news = ak.stock_news_em(symbol=keyword)
        if news is None or len(news) == 0:
            return []
        
        results = []
        for _, row in news.head(max_items).iterrows():
            title = str(row.get('新闻标题', row.get('title', '')))
            content = str(row.get('新闻内容', row.get('content', '')))
            source = str(row.get('文章来源', row.get('source', '')))
            pub_time = str(row.get('发布时间', row.get('publish_time', '')))
            
            sentiment, pos, neg = simple_sentiment(title + content)
            results.append({
                'title': title,
                'source': source,
                'time': pub_time,
                'sentiment': sentiment,
                'pos_count': pos,
                'neg_count': neg,
            })
        return results
    except Exception as e:
        return [{'error': str(e), 'keyword': keyword}]

def fetch_economic_news():
    """获取宏观经济新闻"""
    try:
        news = ak.news_economic_baidu()
        if news is None or len(news) == 0:
            return []
        results = []
        for _, row in news.head(15).iterrows():
            title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
            content = str(row.get('content', row.iloc[1] if len(row) > 1 else ''))
            sentiment, pos, neg = simple_sentiment(title + content)
            results.append({
                'title': title,
                'sentiment': sentiment,
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]

def fetch_cctv_news():
    """获取央视新闻"""
    try:
        news = ak.news_cctv()
        if news is None or len(news) == 0:
            return []
        results = []
        for _, row in news.head(10).iterrows():
            title = str(row.get('title', row.iloc[0] if len(row) > 0 else ''))
            results.append({'title': title})
        return results
    except Exception as e:
        return [{'error': str(e)}]

# ========== 主执行 ==========
print("=" * 60)
print("舆情分析 - 2026-03-04 盘前")
print("=" * 60)

sentiment_data = {
    'date': '2026-03-04',
    'keywords': {},
    'economic_news': [],
    'cctv_news': [],
    'summary': {}
}

# 1. 关键词新闻扫描
print("\n📰 关键词新闻扫描...")
for kw in KEYWORDS:
    print(f"  扫描: {kw}...", end=" ")
    news = fetch_keyword_news(kw, max_items=5)
    sentiment_data['keywords'][kw] = news
    
    if news and 'error' not in news[0]:
        pos = sum(1 for n in news if n.get('sentiment') == 'positive')
        neg = sum(1 for n in news if n.get('sentiment') == 'negative')
        neu = sum(1 for n in news if n.get('sentiment') == 'neutral')
        total = len(news)
        
        if pos > neg:
            overall = '🟢 偏多'
        elif neg > pos:
            overall = '🔴 偏空'
        else:
            overall = '🟡 中性'
        
        sentiment_data['summary'][kw] = {
            'overall': overall,
            'positive': pos,
            'negative': neg,
            'neutral': neu,
            'total': total,
        }
        print(f"{overall} (正:{pos}/负:{neg}/中:{neu})")
    else:
        print("⚠️ 获取失败")
        sentiment_data['summary'][kw] = {'overall': '❓ 无数据', 'error': True}
    
    time.sleep(0.3)  # 避免请求过快

# 2. 宏观经济新闻
print("\n📊 宏观经济新闻...")
sentiment_data['economic_news'] = fetch_economic_news()
print(f"  获取 {len(sentiment_data['economic_news'])} 条")

# 3. 央视新闻
print("\n📺 央视新闻...")
sentiment_data['cctv_news'] = fetch_cctv_news()
print(f"  获取 {len(sentiment_data['cctv_news'])} 条")

# 输出汇总
print("\n" + "=" * 60)
print("📊 舆情汇总")
print("=" * 60)
for kw, info in sentiment_data['summary'].items():
    if not info.get('error'):
        print(f"  {kw:<8} {info['overall']}  (正:{info['positive']}/负:{info['negative']}/中:{info['neutral']})")

# 保存数据
output_path = os.path.join(SCRIPT_DIR, 'sentiment_data.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sentiment_data, f, indent=4, ensure_ascii=False, default=str)

print(f"\n✅ 舆情数据已保存至: {output_path}")

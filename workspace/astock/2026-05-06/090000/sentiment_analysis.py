#!/usr/bin/env python3
"""
舆情分析 — 2026-05-06（五一假期后首个交易日）
"""
import sys, os, json, warnings
warnings.filterwarnings('ignore')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

KEYWORDS = [
    '红利', '医疗', '军工', '5G', 'AI', '光伏', '电力',
    '科创', '半导体', '机器人', '化工',
    '消费', '豆粕', '粮食', '矿业', '电网', '工程机械',
    '航天', '黄金', '白银', '港股', '新能源', '稀土'
]

def simple_sentiment(text):
    pos = ['上涨','突破','利好','增长','创新高','强势','暴涨','反弹','回升',
           '放量','新高','景气','加速','扩产','提价','爆发','飙升','涨停',
           '看好','机遇','布局','加码','超预期','大涨']
    neg = ['下跌','暴跌','利空','风险','下调','疲软','回落','缩量','破位',
           '跌停','减持','亏损','下降','萎缩','担忧','低迷','承压','收缩',
           '走弱','恶化','制裁','限制','抛售','拖累']
    t = str(text)
    pc = sum(1 for w in pos if w in t)
    nc = sum(1 for w in neg if w in t)
    return 'positive' if pc > nc else ('negative' if nc > pc else 'neutral')

def fetch_keyword_news(keyword, max_items=8):
    try:
        import akshare as ak
        df = ak.stock_news_em(symbol=keyword)
        if df is None or df.empty:
            return []
        results = []
        for _, row in df.head(max_items).iterrows():
            title   = str(row.get('新闻标题', row.get('title', '')))
            content = str(row.get('新闻内容', row.get('content', '')))
            source  = str(row.get('文章来源', row.get('source', '')))
            pub     = str(row.get('发布时间', row.get('publish_time', '')))
            results.append({
                'title': title[:120], 'source': source,
                'date': pub, 'sentiment': simple_sentiment(title + ' ' + content)
            })
        return results
    except Exception as e:
        return [{'error': str(e)}]

def fetch_economic_news():
    try:
        import akshare as ak
        df = ak.news_economic_baidu()
        if df is None or df.empty:
            return []
        results = []
        for _, row in df.head(12).iterrows():
            title = str(row.get('title', ''))
            results.append({'title': title[:120], 'sentiment': simple_sentiment(title)})
        return results
    except Exception as e:
        return [{'error': str(e)}]

def main():
    data = {'keywords': {}, 'economic_news': [], 'summary': {}}

    print("=" * 60)
    print("舆情扫描 — Sentiment Scan (2026-05-06)")
    print("=" * 60)

    for kw in KEYWORDS:
        print(f"\n🔍 {kw}...")
        news = fetch_keyword_news(kw)
        if news and 'error' not in news[0]:
            pos = sum(1 for n in news if n.get('sentiment') == 'positive')
            neg = sum(1 for n in news if n.get('sentiment') == 'negative')
            neu = len(news) - pos - neg
            overall = 'positive' if pos > neg and pos >= len(news)*0.4 else (
                      'negative' if neg > pos and neg >= len(news)*0.4 else 'neutral')
            data['keywords'][kw] = {'news': news, 'stats': {'positive': pos, 'negative': neg, 'neutral': neu, 'total': len(news)}, 'overall': overall}
            print(f"   📰 {len(news)}条 | +{pos} ={neu} -{neg} → {overall}")
            for n in news[:3]:
                if 'title' in n:
                    e = '🟢' if n['sentiment']=='positive' else ('🔴' if n['sentiment']=='negative' else '🟡')
                    print(f"   {e} {n['title'][:65]}")
        else:
            data['keywords'][kw] = {'news': news, 'overall': 'unknown'}
            err = news[0].get('error', '无数据') if news else '无数据'
            print(f"   ❌ {err[:60]}")

    print(f"\n{'='*60}\n宏观经济新闻\n{'='*60}")
    econ = fetch_economic_news()
    data['economic_news'] = econ
    for n in econ[:10]:
        if 'title' in n:
            e = '🟢' if n['sentiment']=='positive' else ('🔴' if n['sentiment']=='negative' else '🟡')
            print(f"   {e} {n['title'][:80]}")

    data['summary'] = {kw: v.get('overall','unknown') for kw, v in data['keywords'].items()}

    out = os.path.join(SCRIPT_DIR, 'astock_sentiment_data.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\n✅ 舆情数据已保存: {out}")

if __name__ == '__main__':
    main()

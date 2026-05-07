#!/usr/bin/env python3
"""Fetch sector sentiment data via AKShare for A-stock portfolio analysis."""
import os, json, warnings
warnings.filterwarnings('ignore')
import akshare as ak
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

POSITIVE_WORDS = ['上涨','突破','利好','增长','创新高','强势','爆发','回暖','复苏','新高',
                  '大涨','拉升','反弹','超预期','增速','签约','落地','扶持','重大','创历史',
                  '受益','扩张','放量','加速','提振','走强','飙升','进入','机遇','政策支持']
NEGATIVE_WORDS = ['下跌','暴跌','利空','风险','下调','疲软','大跌','回调','减速','亏损',
                  '下滑','萎缩','崩盘','违约','监管','罚款','下修','压制','拖累','冲击',
                  '回落','跳水','拖累','担忧','警惕','压力','减持','出售','裁员','负债']

def sentiment_score(texts):
    pos, neg = 0, 0
    for text in texts:
        pos += sum(1 for w in POSITIVE_WORDS if w in str(text))
        neg += sum(1 for w in NEGATIVE_WORDS if w in str(text))
    total = pos + neg
    if total == 0:
        return 0.0
    ratio = (pos - neg) / total
    return round(ratio * 2, 2)

SECTORS = {
    "科技/AI/半导体/机器人": ["芯片", "机器人"],
    "新能源/光伏/电力": ["光伏", "新能源"],
    "消费/红利蓝筹": ["消费", "红利"],
    "军工/航空航天": ["军工", "航空"],
    "港股/恒指科技": ["港股", "科技股"],
    "化工/大宗商品": ["化工", "大宗商品"],
    "5G通信": ["5G", "通信"],
    "医药医疗": ["医药", "医疗"],
}

results = {}

print("Fetching sector news via AKShare (stock_news_em)...")
for sector, keywords in SECTORS.items():
    print(f"\n  [{sector}]")
    all_titles = []
    all_content = []
    for kw in keywords:
        try:
            df = ak.stock_news_em(symbol=kw)
            if df is not None and not df.empty:
                titles = df['新闻标题'].head(5).tolist()
                content = df['新闻内容'].head(5).fillna('').tolist()
                all_titles.extend(titles)
                all_content.extend(content)
                print(f"    {kw}: {len(titles)} articles")
            else:
                print(f"    {kw}: no data")
        except Exception as e:
            print(f"    {kw}: error - {e}")

    score = sentiment_score(all_content if all_content else all_titles)
    top_headlines = list(dict.fromkeys(all_titles))[:6]

    results[sector] = {
        "score": score,
        "headlines": top_headlines,
        "article_count": len(all_titles),
    }
    print(f"    Score: {score}, Headlines: {len(top_headlines)}")

# Macro news
print("\n  [宏观/政策]")
macro_headlines = []
try:
    df_cctv = ak.news_cctv(date="20260507")
    if df_cctv is not None and not df_cctv.empty:
        macro_headlines = df_cctv['title'].head(8).tolist()
        print(f"    CCTV: {len(macro_headlines)} news")
    else:
        # Try previous day
        df_cctv = ak.news_cctv(date="20260506")
        if df_cctv is not None and not df_cctv.empty:
            macro_headlines = df_cctv['title'].head(8).tolist()
            print(f"    CCTV (2026-05-06): {len(macro_headlines)} news")
except Exception as e:
    print(f"    CCTV error: {e}")

macro_score = sentiment_score(macro_headlines)
results["宏观/政策"] = {
    "score": macro_score,
    "headlines": macro_headlines,
    "article_count": len(macro_headlines),
}

# Save
output_path = os.path.join(SCRIPT_DIR, "astock_sentiment_data.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\nSaved to {output_path}")
print("\n=== SENTIMENT SUMMARY ===")
for sector, data in results.items():
    score_str = f"+{data['score']}" if data['score'] > 0 else str(data['score'])
    bar = "▲" * max(0, int(data['score'])) if data['score'] > 0 else "▼" * max(0, int(-data['score']))
    print(f"  {sector}: {score_str} {bar}")
    if data['headlines']:
        print(f"    Top: {data['headlines'][0][:60]}")

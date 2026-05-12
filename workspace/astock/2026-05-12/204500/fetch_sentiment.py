#!/usr/bin/env python3
"""Fetch news sentiment for A-stock ETF themes via AkShare."""
import os, json, sys, warnings
warnings.filterwarnings("ignore")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import akshare as ak
import pandas as pd

POSITIVE_WORDS = ["上涨", "突破", "利好", "增长", "创新高", "强势", "反弹", "回暖", "复苏",
                  "提振", "扩张", "政策支持", "加速", "超预期", "利润增", "景气", "受益"]
NEGATIVE_WORDS = ["下跌", "暴跌", "利空", "风险", "下调", "疲软", "萎缩", "亏损", "担忧",
                  "收缩", "通缩", "关税", "打压", "制裁", "退市", "业绩下滑", "警示"]

def simple_sentiment(text: str) -> tuple[float, str]:
    pos = sum(1 for w in POSITIVE_WORDS if w in text)
    neg = sum(1 for w in NEGATIVE_WORDS if w in text)
    total = pos + neg
    if total == 0:
        return 0.0, "neutral"
    score = (pos - neg) / total
    label = "positive" if score > 0.1 else ("negative" if score < -0.1 else "neutral")
    return round(score, 2), label

def fetch_news(symbol: str, max_n: int = 5):
    """Fetch news from dongfangcafu via akshare."""
    try:
        df = ak.stock_news_em(symbol=symbol)
        if df is None or df.empty:
            return []
        rows = []
        for _, row in df.head(max_n).iterrows():
            title = str(row.get("新闻标题", row.get("title", "")))
            content = str(row.get("新闻内容", row.get("content", "")))
            text = title + content
            score, label = simple_sentiment(text)
            rows.append({"title": title, "sentiment": label, "score": score})
        return rows
    except Exception as e:
        return [{"error": str(e)}]

TOPICS = {
    "macro_astock":    ("A股市场", ["A股", "大盘", "指数", "市场"]),
    "macro_trade":     ("中美贸易", ["关税", "贸易战", "中美", "谈判"]),
    "sector_consumer": ("消费ETF", ["消费", "内需", "零售", "白酒"]),
    "sector_dividend": ("红利ETF", ["红利", "高股息", "分红", "蓝筹"]),
    "sector_healthcare":("医疗ETF", ["医药", "医疗", "创新药", "集采"]),
    "sector_defense":  ("军工ETF", ["军工", "国防", "军事", "武器"]),
    "sector_hk_tech":  ("港股科技", ["恒生科技", "港股", "互联网", "腾讯"]),
    "sector_5g":       ("5G通信", ["5G", "通信", "基站", "运营商"]),
    "sector_ai":       ("AI人工智能", ["人工智能", "AI", "大模型", "算力"]),
    "sector_solar":    ("光伏ETF", ["光伏", "太阳能", "新能源", "组件"]),
    "sector_power":    ("电力ETF", ["电力", "公用事业", "发电", "电网"]),
    "sector_semicon":  ("半导体设备", ["半导体", "芯片", "光刻机", "设备"]),
    "sector_robot":    ("机器人AI", ["机器人", "人形机器人", "工业机器人"]),
    "sector_chem":     ("化工ETF", ["化工", "基础化工", "化学品"]),
    "sector_soybean":  ("豆粕ETF", ["豆粕", "大豆", "饲料", "农产品"]),
    "sector_grain":    ("粮食ETF", ["粮食", "小麦", "玉米", "农业"]),
    "sector_mining":   ("矿业ETF", ["铜", "铝", "矿业", "有色金属"]),
    "sector_grid":     ("电网设备", ["电网", "特高压", "变压器", "电力设备"]),
    "sector_machinery":("工程机械", ["工程机械", "挖掘机", "起重机"]),
    "sector_aerospace":("航空航天", ["航空航天", "商业航天", "火箭", "卫星"]),
    "sector_gold":     ("黄金", ["黄金", "金价", "避险", "美联储"]),
    "sector_silver":   ("白银", ["白银", "贵金属", "银价"]),
    "sector_kcb50":    ("科创50", ["科创板", "科创50", "硬科技"]),
}

results = {}
for key, (primary_kw, alt_keywords) in TOPICS.items():
    print(f"Fetching news: {primary_kw}...")
    news_items = fetch_news(primary_kw, max_n=5)
    if not news_items or (len(news_items) == 1 and "error" in news_items[0]):
        for kw in alt_keywords:
            news_items = fetch_news(kw, max_n=5)
            if news_items and not (len(news_items) == 1 and "error" in news_items[0]):
                print(f"  fallback to '{kw}'")
                break
    # aggregate sentiment
    valid = [n for n in news_items if "score" in n]
    if valid:
        avg_score = sum(n["score"] for n in valid) / len(valid)
        overall = "positive" if avg_score > 0.1 else ("negative" if avg_score < -0.1 else "neutral")
    else:
        avg_score, overall = 0.0, "neutral"
    results[key] = {
        "query": primary_kw,
        "sentiment_score": round(avg_score, 2),
        "sentiment_label": overall,
        "news": news_items,
    }
    print(f"  score={avg_score:.2f} ({overall}), {len(valid)} articles")

# Also fetch macro news
print("\nFetching Baidu economic news...")
try:
    eco_df = ak.news_economic_baidu()
    macro_news = []
    for _, row in eco_df.head(8).iterrows():
        title = str(row.get("title", row.get("新闻标题", "")))
        score, label = simple_sentiment(title)
        macro_news.append({"title": title, "sentiment": label, "score": score})
    results["baidu_macro_news"] = {"news": macro_news}
    print(f"  Got {len(macro_news)} items")
except Exception as e:
    results["baidu_macro_news"] = {"error": str(e)}
    print(f"  ERROR: {e}")

out_path = os.path.join(SCRIPT_DIR, "astock_sentiment_data.json")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print(f"\n✅ Saved sentiment to {out_path}")

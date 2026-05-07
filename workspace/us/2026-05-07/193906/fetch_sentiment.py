#!/usr/bin/env python3
"""Fetch US stock news sentiment via AkShare and web search."""
import sys, os, json
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

TICKERS_KEYWORDS = {
    'US.PLTR': ['Palantir', 'PLTR'],
    'US.CRCL': ['Circle', 'CRCL', 'USDC stablecoin'],
    'US.RKLB': ['Rocket Lab', 'RKLB', 'space launch'],
    'US.AMD': ['AMD', 'Advanced Micro Devices'],
    'US.TSLA': ['Tesla', 'TSLA', 'Elon Musk'],
    'US.SLV': ['silver', 'SLV'],
    'US.GOOG': ['Google', 'Alphabet', 'GOOG'],
    'US.IAU': ['gold', 'IAU', 'gold ETF'],
    'US.TSM': ['TSMC', 'Taiwan Semiconductor', 'TSM'],
    'US.NVDA': ['NVIDIA', 'NVDA'],
}

MACRO_KEYWORDS = ['Fed', 'Federal Reserve', 'tariff', 'trade war', 'inflation', 'CPI', 'rate cut', 'S&P 500', 'AI chip']

def fetch_news_akshare(keyword):
    """Fetch news from East Money using AkShare."""
    try:
        import akshare as ak
        news_df = ak.stock_news_em(symbol=keyword)
        if news_df is not None and len(news_df) > 0:
            results = []
            for _, row in news_df.head(3).iterrows():
                results.append({
                    'title': str(row.get('新闻标题', row.get('title', ''))),
                    'date': str(row.get('发布时间', row.get('date', ''))),
                    'source': 'eastmoney',
                })
            return results
    except Exception as e:
        pass
    return []

def simple_sentiment(text):
    """Simple keyword-based sentiment scoring for US stocks."""
    pos = ['beat', 'surge', 'jump', 'rally', 'growth', 'profit', 'upgrade', 'buy',
           'record', 'outperform', 'bullish', 'strong', 'win', 'deal', '上涨', '利好', '突破']
    neg = ['miss', 'drop', 'fall', 'crash', 'loss', 'downgrade', 'sell', 'risk',
           'warning', 'bearish', 'weak', 'cut', 'tariff', 'ban', '下跌', '利空', '风险']
    text_lower = text.lower()
    pos_c = sum(1 for w in pos if w.lower() in text_lower)
    neg_c = sum(1 for w in neg if w.lower() in text_lower)
    if pos_c > neg_c: return 'positive'
    elif neg_c > pos_c: return 'negative'
    return 'neutral'

def main():
    print("Fetching sentiment data...")
    results = {}

    # Macro news
    print("  Fetching macro news...")
    try:
        import akshare as ak
        eco_news = ak.news_economic_baidu()
        macro_items = []
        if eco_news is not None:
            for _, row in eco_news.head(8).iterrows():
                title = str(row.get('title', row.get('新闻标题', '')))
                macro_items.append({
                    'title': title,
                    'date': str(row.get('date', row.get('发布时间', ''))),
                    'sentiment': simple_sentiment(title),
                })
        results['macro'] = macro_items
        print(f"    Got {len(macro_items)} macro news")
    except Exception as e:
        print(f"    Macro news error: {e}")
        results['macro'] = []

    # Per-ticker
    for ticker, keywords in TICKERS_KEYWORDS.items():
        print(f"  Fetching {ticker} ({keywords[0]})...")
        ticker_news = []
        for kw in keywords[:1]:
            news = fetch_news_akshare(kw)
            ticker_news.extend(news)
            if ticker_news:
                break

        sentiments = [simple_sentiment(n['title']) for n in ticker_news]
        pos = sentiments.count('positive')
        neg = sentiments.count('negative')
        overall = 'positive' if pos > neg else ('negative' if neg > pos else 'neutral')

        results[ticker] = {
            'news': ticker_news,
            'sentiment': overall,
            'pos_count': pos,
            'neg_count': neg,
        }
        print(f"    {len(ticker_news)} articles, sentiment={overall}")

    results['fetch_time'] = datetime.now().isoformat()

    out_path = os.path.join(SCRIPT_DIR, 'us_sentiment_data.json')
    with open(out_path, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to {out_path}")
    return results

if __name__ == '__main__':
    main()

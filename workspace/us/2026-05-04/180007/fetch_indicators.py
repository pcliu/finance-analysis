import sys, os, json
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

from dotenv import load_dotenv
load_dotenv(os.path.join(SCRIPT_DIR, '../../../../.env.local'))

from scripts import (
    get_realtime_quote, get_kline_data,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_ema, calculate_atr,
    make_serializable
)

WATCHLIST = ['US.RKLB', 'US.AMD', 'US.TSLA', 'US.SLV', 'US.GOOG', 'US.IAU', 'US.TSM', 'US.NVDA']

# Real-time quotes
print("Fetching real-time quotes...")
quotes = get_realtime_quote(WATCHLIST)
print(json.dumps(make_serializable(quotes), ensure_ascii=False, indent=2))

# Technical indicators for each ticker
print("\n=== TECHNICAL INDICATORS ===")
all_indicators = {}

for ticker in WATCHLIST:
    print(f"\nProcessing {ticker}...")
    try:
        kline = get_kline_data(ticker, count=150)
        if kline is None or len(kline) < 30:
            print(f"  Insufficient data for {ticker}")
            continue

        rsi = calculate_rsi(kline, window=14)
        macd_df = calculate_macd(kline)
        bb = calculate_bollinger_bands(kline)
        sma20 = calculate_sma(kline, window=20)
        sma50 = calculate_sma(kline, window=50)
        ema20 = calculate_ema(kline, window=20)
        atr = calculate_atr(kline, window=14)

        # Volume analysis: current vs 20-day avg
        vol_avg20 = kline['Volume'].tail(21).iloc[:-1].mean()
        vol_latest = kline['Volume'].iloc[-1]
        vol_ratio = vol_latest / vol_avg20 if vol_avg20 > 0 else None

        last = kline.iloc[-1]
        indicators = {
            'ticker': ticker,
            'close': round(float(last['Close']), 4),
            'open': round(float(last['Open']), 4),
            'high': round(float(last['High']), 4),
            'low': round(float(last['Low']), 4),
            'volume': int(last['Volume']),
            'vol_avg20': round(float(vol_avg20), 0),
            'vol_ratio': round(float(vol_ratio), 2) if vol_ratio else None,
            'rsi14': round(float(rsi['RSI'].iloc[-1]), 2) if 'RSI' in rsi.columns else None,
            'macd': round(float(macd_df['MACD'].iloc[-1]), 4) if 'MACD' in macd_df.columns else None,
            'macd_signal': round(float(macd_df['Signal'].iloc[-1]), 4) if 'Signal' in macd_df.columns else None,
            'macd_hist': round(float(macd_df['Histogram'].iloc[-1]), 4) if 'Histogram' in macd_df.columns else None,
            'bb_upper': round(float(bb['Upper'].iloc[-1]), 4) if 'Upper' in bb.columns else None,
            'bb_middle': round(float(bb['Middle'].iloc[-1]), 4) if 'Middle' in bb.columns else None,
            'bb_lower': round(float(bb['Lower'].iloc[-1]), 4) if 'Lower' in bb.columns else None,
            'bb_pct_b': round(float(bb['%B'].iloc[-1]), 4) if '%B' in bb.columns else None,
            'sma20': round(float(sma20['SMA'].iloc[-1]), 4) if 'SMA' in sma20.columns else None,
            'sma50': round(float(sma50['SMA'].iloc[-1]), 4) if 'SMA' in sma50.columns else None,
            'ema20': round(float(ema20['EMA'].iloc[-1]), 4) if 'EMA' in ema20.columns else None,
            'atr14': round(float(atr['ATR'].iloc[-1]), 4) if 'ATR' in atr.columns else None,
            # Prior day RSI for trend
            'rsi14_prev': round(float(rsi['RSI'].iloc[-2]), 2) if 'RSI' in rsi.columns and len(rsi) > 1 else None,
            'macd_hist_prev': round(float(macd_df['Histogram'].iloc[-2]), 4) if 'Histogram' in macd_df.columns and len(macd_df) > 1 else None,
        }

        all_indicators[ticker] = indicators
        print(f"  RSI={indicators['rsi14']}, MACD_hist={indicators['macd_hist']}, %B={indicators['bb_pct_b']}, Close={indicators['close']}")
    except Exception as e:
        print(f"  Error for {ticker}: {e}")
        import traceback; traceback.print_exc()

# Save indicators to JSON
out_path = os.path.join(SCRIPT_DIR, 'us_indicators_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(all_indicators, f, ensure_ascii=False, indent=2)
print(f"\nSaved indicators to {out_path}")

"""Fetch AUDCNY history + compute technical indicators."""
import sys, os, json
import pandas as pd
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append('/Users/liupengcheng/Code/finance-analysis/.claude/skills/quantitative-trading')

import yfinance as yf
from scripts.indicators import TechnicalIndicators
ti = TechnicalIndicators()
calculate_rsi = ti.calculate_rsi
calculate_macd = ti.calculate_macd
calculate_bollinger_bands = ti.calculate_bollinger_bands
calculate_sma = ti.calculate_sma
calculate_ema = ti.calculate_ema
calculate_atr = ti.calculate_atr

# Yahoo symbol for AUD/CNY
df = yf.download('AUDCNY=X', period='2y', interval='1d', auto_adjust=False, progress=False)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.dropna()
print(f"Rows: {len(df)}, Last date: {df.index[-1].date()}")
print(df.tail(10)[['Open','High','Low','Close']].round(4))

last = df['Close'].iloc[-1]
print(f"\nLatest AUDCNY close: {last:.4f}")

# indicators
rsi = calculate_rsi(df, window=14)
macd = calculate_macd(df)
bb = calculate_bollinger_bands(df, window=20)
sma20 = calculate_sma(df, window=20)
sma50 = calculate_sma(df, window=50)
sma200 = calculate_sma(df, window=200)
ema12 = calculate_ema(df, window=12)
atr = calculate_atr(df, window=14)

summary = {
    'last_date': str(df.index[-1].date()),
    'close': round(float(last), 4),
    'rsi14': round(float(rsi['RSI'].iloc[-1]), 2),
    'macd': round(float(macd['MACD'].iloc[-1]), 4),
    'macd_signal': round(float(macd['Signal'].iloc[-1]), 4),
    'macd_hist': round(float(macd['Histogram'].iloc[-1]), 4),
    'bb_upper': round(float(bb['Upper'].iloc[-1]), 4),
    'bb_middle': round(float(bb['Middle'].iloc[-1]), 4),
    'bb_lower': round(float(bb['Lower'].iloc[-1]), 4),
    'bb_pct': round(float(bb['Percent_B'].iloc[-1]), 3),
    'sma20': round(float(sma20['SMA'].iloc[-1]), 4),
    'sma50': round(float(sma50['SMA'].iloc[-1]), 4),
    'sma200': round(float(sma200['SMA'].iloc[-1]), 4),
    'ema12': round(float(ema12['EMA'].iloc[-1]), 4),
    'atr14': round(float(atr['ATR'].iloc[-1]), 4),
}

# Stats over different windows
for window, label in [(20, '1m'), (60, '3m'), (120, '6m'), (252, '1y')]:
    sub = df['Close'].tail(window)
    summary[f'high_{label}'] = round(float(sub.max()), 4)
    summary[f'low_{label}']  = round(float(sub.min()), 4)
    summary[f'mean_{label}'] = round(float(sub.mean()), 4)
    # percentile of current
    rank = (sub <= last).sum() / len(sub)
    summary[f'pctile_{label}'] = round(float(rank), 3)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))

with open(os.path.join(SCRIPT_DIR, 'audcny_data.json'), 'w') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

# Save tail csv
df.tail(120).to_csv(os.path.join(SCRIPT_DIR, 'audcny_tail120.csv'))
print(f"\nSaved to {SCRIPT_DIR}")

#!/usr/bin/env python3
"""Fetch realtime ETF quotes via AKShare ETF-specific interface."""
import os, json, warnings
warnings.filterwarnings('ignore')
import akshare as ak

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

SYMBOLS = [
    "510150","510880","512170","512660","513180","515050","515070",
    "515790","561560","588000","159516","159770","159870",
    "159985","159689","561330","159326","560280","159241","159830","161226","513630"
]

print("Fetching ETF realtime quotes...")
try:
    df = ak.fund_etf_spot_em()
    print(f"Columns: {list(df.columns)}")
    print(f"Sample codes: {df['代码'].head(10).tolist()}")
except Exception as e:
    print(f"fund_etf_spot_em error: {e}")
    df = None

results = {}

if df is not None:
    for sym in SYMBOLS:
        row = df[df['代码'] == sym]
        if not row.empty:
            r = row.iloc[0]
            results[sym] = {
                "price": float(r.get('最新价', r.get('现价', 0))),
                "pct_chg": float(r.get('涨跌幅', 0)),
                "volume": float(r.get('成交量', 0)),
                "amount": float(r.get('成交额', 0)),
            }
            print(f"  {sym}: {results[sym]}")
        else:
            print(f"  {sym}: not found")

# Also try lof spot data for LOF funds
try:
    df_lof = ak.fund_lof_spot_em()
    row = df_lof[df_lof['代码'] == '161226']
    if not row.empty:
        r = row.iloc[0]
        results['161226'] = {
            "price": float(r.get('最新价', r.get('现价', 0))),
            "pct_chg": float(r.get('涨跌幅', 0)),
        }
        print(f"  161226 (LOF): {results['161226']}")
except Exception as e:
    print(f"LOF error: {e}")

# Save
indicators_path = os.path.join(SCRIPT_DIR, "astock_indicators_data.json")
with open(indicators_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for sym, rt in results.items():
    if sym in data:
        data[sym]["realtime"] = rt

with open(indicators_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print(f"\nUpdated {indicators_path}")

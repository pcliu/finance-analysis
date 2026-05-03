import sys, os, json, traceback
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.claude/skills/moomoo-trading'))
sys.path.append(SKILL_DIR)

HOST = '127.0.0.1'
PORT = 11111

results = {
    "timestamp": datetime.now().isoformat(),
    "opend": f"{HOST}:{PORT}",
    "tests": {}
}

def ok(name, detail=""):
    results["tests"][name] = {"status": "✅ PASS", "detail": str(detail)}
    print(f"  ✅ {name}: {detail}")

def fail(name, err):
    results["tests"][name] = {"status": "❌ FAIL", "detail": str(err)}
    print(f"  ❌ {name}: {err}")

print("=" * 55)
print("  Moomoo OpenD Connection Validation")
print(f"  Target: {HOST}:{PORT}")
print("=" * 55)

# ── 1. Import ──────────────────────────────────────────────
print("\n[1] Import moomoo-api")
try:
    import moomoo as ft
    ok("import", f"moomoo-api version loaded")
except ImportError as e:
    fail("import", e)
    sys.exit(1)

# ── 2. Quote connection ────────────────────────────────────
print("\n[2] Quote connection (QuoteCtx)")
quote_ctx = None
try:
    quote_ctx = ft.OpenQuoteContext(host=HOST, port=PORT)
    ok("QuoteCtx", "connected")
except Exception as e:
    fail("QuoteCtx", e)

# ── 3. Real-time snapshot ──────────────────────────────────
print("\n[3] Real-time snapshot — US.NVDA, US.AMD, US.GOOG")
if quote_ctx:
    try:
        ret, data = quote_ctx.get_market_snapshot(['US.NVDA', 'US.AMD', 'US.GOOG'])
        if ret == ft.RET_OK:
            rows = []
            chg_col = 'change_rate' if 'change_rate' in data.columns else ('price_change_ratio' if 'price_change_ratio' in data.columns else None)
            for _, row in data.iterrows():
                chg = f"{row[chg_col]:.2f}%" if chg_col else "N/A"
                rows.append({"ticker": row['code'], "last_price": row['last_price'], "change": chg})
                print(f"     {row['code']:12s}  last={row['last_price']}  chg={chg}")
            ok("snapshot", f"{len(rows)} tickers")
            results["snapshot"] = rows
        else:
            fail("snapshot", data)
    except Exception as e:
        fail("snapshot", traceback.format_exc())

# ── 4. K-line data ─────────────────────────────────────────
print("\n[4] K-line data — US.NVDA daily 5 bars")
if quote_ctx:
    try:
        ret, data, _ = quote_ctx.request_history_kline(
            'US.NVDA', ktype=ft.KLType.K_DAY, autype=ft.AuType.QFQ,
            fields=[ft.KL_FIELD.ALL], max_count=5
        )
        if ret == ft.RET_OK:
            last = data.iloc[-1]
            date_val = last.get('time_key', last.get('date', 'N/A'))
            if hasattr(date_val, '__str__'):
                date_val = str(date_val)[:10]
            print(f"     Latest bar: date={date_val}  close={last['close']}  vol={last['volume']}")
            ok("kline", f"{len(data)} bars")
        else:
            fail("kline", data)
    except Exception as e:
        fail("kline", traceback.format_exc())

if quote_ctx:
    quote_ctx.close()

# ── 5. Trade connection (SIMULATE) ─────────────────────────
print("\n[5] Trade connection — SIMULATE account")
trade_ctx = None
try:
    trade_ctx = ft.OpenSecTradeContext(
        filter_trdmarket=ft.TrdMarket.US,
        host=HOST, port=PORT,
        security_firm=ft.SecurityFirm.FUTUSECURITIES
    )
    ok("TradeCtx", "connected")
except Exception as e:
    fail("TradeCtx", e)

# ── 6. Account info ────────────────────────────────────────
print("\n[6] Account info — SIMULATE")
if trade_ctx:
    try:
        ret, data = trade_ctx.accinfo_query(trd_env=ft.TrdEnv.SIMULATE)
        if ret == ft.RET_OK:
            row = data.iloc[0]
            info = {
                "total_assets": row.get('total_assets', 'N/A'),
                "cash": row.get('cash', 'N/A'),
                "market_val": row.get('market_val', 'N/A'),
            }
            for k, v in info.items():
                print(f"     {k}: {v}")
            ok("account_info", "OK")
            results["account"] = {k: str(v) for k, v in info.items()}
        else:
            fail("account_info", data)
    except Exception as e:
        fail("account_info", traceback.format_exc())

# ── 7. Positions ───────────────────────────────────────────
print("\n[7] Positions — SIMULATE")
if trade_ctx:
    try:
        ret, data = trade_ctx.position_list_query(trd_env=ft.TrdEnv.SIMULATE)
        if ret == ft.RET_OK:
            if len(data) == 0:
                print("     (no open positions)")
            else:
                for _, row in data.iterrows():
                    print(f"     {row['code']:12s}  qty={row['qty']}  cost={row['cost_price']}  mkt_val={row['market_val']}")
            ok("positions", f"{len(data)} position(s)")
        else:
            fail("positions", data)
    except Exception as e:
        fail("positions", traceback.format_exc())

if trade_ctx:
    trade_ctx.close()

# ── Summary ────────────────────────────────────────────────
print("\n" + "=" * 55)
passed = sum(1 for v in results["tests"].values() if "PASS" in v["status"])
total  = len(results["tests"])
print(f"  Result: {passed}/{total} tests passed")
print("=" * 55)

out = os.path.join(SCRIPT_DIR, "moomoo_validate_data.json")
with open(out, "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\n  Report saved → {out}")

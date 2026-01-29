#!/usr/bin/env python3
"""
持仓调整技术分析脚本
生成时间：2026-01-27 09:03:32
分析周期：计算RSI、布林带、MACD等核心技术指标
"""

import sys
import os
import json
from datetime import datetime

# Robust Import: Use absolute path relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma
from scripts.utils import make_serializable

# 当前持仓 (根据用户截图)
CURRENT_HOLDINGS = {
    "510150": {"name": "消费ETF", "shares": 10000, "cost": 0.5721, "current_price": 0.5550, "pnl_pct": -2.99},
    "510880": {"name": "红利ETF", "shares": 8500, "cost": 3.0589, "current_price": 3.1060, "pnl_pct": 1.54},
    "512660": {"name": "军工ETF", "shares": 6000, "cost": 1.5276, "current_price": 1.5030, "pnl_pct": -1.61},
    "513180": {"name": "恒指科技", "shares": 800, "cost": 0.7686, "current_price": 0.7540, "pnl_pct": -1.90},
    "515050": {"name": "5GETF", "shares": 1000, "cost": 2.3200, "current_price": 2.3320, "pnl_pct": 0.52},
    "515070": {"name": "AI智能", "shares": 400, "cost": 1.9388, "current_price": 2.0980, "pnl_pct": 8.21},
    "588000": {"name": "科创50", "shares": 1000, "cost": 0.3019, "current_price": 1.6150, "pnl_pct": 434.95},
    "159241": {"name": "航空TH", "shares": 6000, "cost": 1.5319, "current_price": 1.5030, "pnl_pct": -1.89},
    "159770": {"name": "机器人AI", "shares": 200, "cost": 0.7670, "current_price": 1.1370, "pnl_pct": 48.24},
}

# ETFs.csv 中的全部标的
ALL_ETFS = [
    ("510150", "消费ETF"),
    ("512660", "军工ETF"),
    ("159241", "航空航天ETF"),
    ("159206", "卫星ETF"),
    ("515790", "光伏ETF"),
    ("516780", "稀土ETF"),
    ("512170", "医疗ETF"),
    ("561330", "矿业ETF"),
    ("159870", "化工ETF"),
    ("561560", "电力ETF"),
    ("159830", "上海金ETF"),
    ("159770", "机器人ETF"),
    ("515070", "人工智能AI"),
    ("159326", "电网设备ETF"),
    ("159516", "半导体设备ETF"),
    ("515050", "通信ETF"),
    ("161226", "国投白银LOF"),
    ("518880", "黄金ETF"),
    ("512400", "有色金属ETF"),
    ("510880", "红利ETF"),
    ("513180", "恒生科技指数ETF"),
    ("513630", "港股红利指数ETF"),
    ("588000", "科创50ETF"),
]

def analyze_single_ticker(code, name):
    """分析单个标的的技术指标"""
    try:
        # Fetch 60 days of data for indicators
        data = fetch_stock_data(code, period='3mo')
        if data is None or len(data) < 25:
            return {"error": f"Data insufficient for {code}"}
        
        # Calculate indicators
        rsi_6 = calculate_rsi(data, window=6)
        rsi_14 = calculate_rsi(data, window=14)
        macd_df = calculate_macd(data)
        bb = calculate_bollinger_bands(data, window=20)
        sma_20 = calculate_sma(data, window=20)
        sma_5 = calculate_sma(data, window=5)
        
        # Get latest values
        current_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2]) if len(data) > 1 else current_price
        price_change_pct = (current_price - prev_price) / prev_price * 100 if prev_price != 0 else 0
        
        # Price 20 days ago for trend
        price_20d_ago = float(data['Close'].iloc[-20]) if len(data) >= 20 else float(data['Close'].iloc[0])
        change_20d_pct = (current_price - price_20d_ago) / price_20d_ago * 100 if price_20d_ago != 0 else 0
        
        # Volume analysis
        avg_volume_5d = data['Volume'].tail(5).mean()
        current_volume = float(data['Volume'].iloc[-1])
        volume_ratio = current_volume / avg_volume_5d if avg_volume_5d > 0 else 1.0
        
        # Bollinger Band %B calculation
        upper_band = float(bb['Upper'].iloc[-1])
        lower_band = float(bb['Lower'].iloc[-1])
        middle_band = float(bb['Middle'].iloc[-1])
        band_width = upper_band - lower_band
        pct_b = (current_price - lower_band) / band_width if band_width > 0 else 0.5
        
        result = {
            "code": code,
            "name": name,
            "current_price": round(current_price, 4),
            "prev_close": round(prev_price, 4),
            "price_change_pct": round(price_change_pct, 2),
            "change_20d_pct": round(change_20d_pct, 2),
            "rsi_6": round(float(rsi_6['RSI'].iloc[-1]), 2) if not rsi_6['RSI'].isna().iloc[-1] else None,
            "rsi_14": round(float(rsi_14['RSI'].iloc[-1]), 2) if not rsi_14['RSI'].isna().iloc[-1] else None,
            "macd": round(float(macd_df['MACD'].iloc[-1]), 4) if not macd_df['MACD'].isna().iloc[-1] else None,
            "macd_signal": round(float(macd_df['Signal'].iloc[-1]), 4) if not macd_df['Signal'].isna().iloc[-1] else None,
            "macd_histogram": round(float(macd_df['Histogram'].iloc[-1]), 4) if not macd_df['Histogram'].isna().iloc[-1] else None,
            "bb_upper": round(upper_band, 4),
            "bb_middle": round(middle_band, 4),
            "bb_lower": round(lower_band, 4),
            "pct_b": round(pct_b, 2),
            "sma_20": round(float(sma_20['SMA'].iloc[-1]), 4) if not sma_20['SMA'].isna().iloc[-1] else None,
            "sma_5": round(float(sma_5['SMA'].iloc[-1]), 4) if not sma_5['SMA'].isna().iloc[-1] else None,
            "volume_ratio": round(volume_ratio, 2),
        }
        return result
    except Exception as e:
        return {"code": code, "name": name, "error": str(e)}

def main():
    print("=" * 60)
    print("持仓调整技术分析程序")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    all_results = []
    
    # Analyze all ETFs
    for code, name in ALL_ETFS:
        print(f"正在分析: {code} {name}...")
        result = analyze_single_ticker(code, name)
        result["is_holding"] = code in CURRENT_HOLDINGS
        if code in CURRENT_HOLDINGS:
            result["holding_info"] = CURRENT_HOLDINGS[code]
        all_results.append(result)
    
    # Sort by RSI (low first for buy opportunities)
    valid_results = [r for r in all_results if "error" not in r]
    invalid_results = [r for r in all_results if "error" in r]
    
    # Categorize by RSI zones
    extreme_overbought = [r for r in valid_results if r["rsi_6"] is not None and r["rsi_6"] > 80]
    overbought = [r for r in valid_results if r["rsi_6"] is not None and 70 < r["rsi_6"] <= 80]
    healthy = [r for r in valid_results if r["rsi_6"] is not None and 40 <= r["rsi_6"] <= 70]
    oversold = [r for r in valid_results if r["rsi_6"] is not None and 30 <= r["rsi_6"] < 40]
    extreme_oversold = [r for r in valid_results if r["rsi_6"] is not None and r["rsi_6"] < 30]
    
    output = {
        "analysis_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "current_holdings": CURRENT_HOLDINGS,
        "categorized": {
            "extreme_overbought": sorted(extreme_overbought, key=lambda x: x["rsi_6"], reverse=True),
            "overbought": sorted(overbought, key=lambda x: x["rsi_6"], reverse=True),
            "healthy": sorted(healthy, key=lambda x: x["rsi_6"], reverse=True),
            "oversold": sorted(oversold, key=lambda x: x["rsi_6"]),
            "extreme_oversold": sorted(extreme_oversold, key=lambda x: x["rsi_6"]),
        },
        "all_results": all_results,
        "errors": invalid_results,
    }
    
    # Serialize and save
    clean_output = make_serializable(output)
    output_file = os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clean_output, f, indent=4, ensure_ascii=False)
    
    print(f"\n数据已保存至: {output_file}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("分析结果汇总")
    print("=" * 60)
    
    print(f"\n🔴 极度超买区 (RSI>80): {len(extreme_overbought)} 个")
    for r in extreme_overbought[:5]:
        print(f"  - {r['code']} {r['name']}: RSI(6)={r['rsi_6']}, %B={r['pct_b']}, 价格={r['current_price']}")
    
    print(f"\n🟠 超买区 (70<RSI≤80): {len(overbought)} 个")
    for r in overbought:
        print(f"  - {r['code']} {r['name']}: RSI(6)={r['rsi_6']}, %B={r['pct_b']}, 价格={r['current_price']}")
    
    print(f"\n✅ 健康区 (40≤RSI≤70): {len(healthy)} 个")
    for r in healthy:
        print(f"  - {r['code']} {r['name']}: RSI(6)={r['rsi_6']}, %B={r['pct_b']}, 价格={r['current_price']}")
    
    print(f"\n🟡 超卖区 (30≤RSI<40): {len(oversold)} 个")
    for r in oversold:
        print(f"  - {r['code']} {r['name']}: RSI(6)={r['rsi_6']}, %B={r['pct_b']}, 价格={r['current_price']}")
    
    print(f"\n🟢 极度超卖区 (RSI<30): {len(extreme_oversold)} 个")
    for r in extreme_oversold:
        print(f"  - {r['code']} {r['name']}: RSI(6)={r['rsi_6']}, %B={r['pct_b']}, 价格={r['current_price']}")
    
    if invalid_results:
        print(f"\n⚠️ 数据获取失败: {len(invalid_results)} 个")
        for r in invalid_results:
            print(f"  - {r['code']} {r['name']}: {r.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("分析完成！请查看 portfolio_adjustment_data.json 获取详细数据")
    print("=" * 60)

if __name__ == "__main__":
    main()

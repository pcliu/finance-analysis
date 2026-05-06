import sys
import os
import json
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_stock_data, calculate_rsi, calculate_macd, calculate_bollinger_bands, calculate_sma
from scripts.utils import make_serializable

def analyze_ticker(ticker):
    try:
        data = fetch_stock_data(ticker, period='1y')
        if data is None or data.empty:
            return {"error": "No data"}
            
        rsi = calculate_rsi(data, window=14)
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data)
        
        # Calculate volume MA
        vol = data['Volume'].astype(float)
        vol_ma20 = vol.rolling(window=20).mean()
        vol_ratio = (vol.iloc[-1] / vol_ma20.iloc[-1]) if vol_ma20.iloc[-1] > 0 else 0
        
        last_price = float(data['Close'].iloc[-1])
        
        result = {
            "price": last_price,
            "rsi": rsi['RSI'].iloc[-1] if not rsi.empty else None,
            "macd": macd['MACD'].iloc[-1] if not macd.empty else None,
            "macd_signal": macd['Signal'].iloc[-1] if not macd.empty else None,
            "macd_hist": macd['Histogram'].iloc[-1] if not macd.empty else None,
            "bb_upper": bb['Upper'].iloc[-1] if not bb.empty else None,
            "bb_lower": bb['Lower'].iloc[-1] if not bb.empty else None,
            "bb_middle": bb['Middle'].iloc[-1] if not bb.empty else None,
            "vol_ratio": float(vol_ratio)
        }
        
        if result['bb_upper'] and result['bb_lower'] and result['bb_upper'] > result['bb_lower']:
            result['bb_pct'] = (last_price - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'])
        else:
            result['bb_pct'] = None
            
        return result
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

def main():
    holdings = {
        "510880": "红利ETF",
        "512170": "医疗ETF",
        "512660": "军工ETF",
        "515050": "5GETF",
        "515070": "AI智能",
        "515790": "光伏ETF",
        "561560": "电力ETF",
        "588000": "科创50",
        "159516": "半导设备",
        "159770": "机器人AI",
        "159870": "化工ETF"
    }
    
    watchlist = {
        "510150": "消费 ETF",
        "159985": "豆粕 ETF",
        "159689": "粮食 ETF",
        "561330": "矿业 ETF",
        "159326": "电网设备 ETF",
        "560280": "工程机械ETF",
        "159241": "航空航天 ETF 天弘",
        "159830": "上海金 ETF",
        "161226": "国投白银 LOF",
        "513180": "恒生科技指数 ETF",
        "513630": "港股红利指数 ETF"
    }
    
    results = {"holdings": {}, "watchlist": {}}
    
    for ticker, name in holdings.items():
        print(f"Analyzing {name} ({ticker})...")
        results["holdings"][name] = analyze_ticker(ticker)
        
    for ticker, name in watchlist.items():
        print(f"Analyzing {name} ({ticker})...")
        results["watchlist"][name] = analyze_ticker(ticker)
        
    clean_results = make_serializable(results)
    
    with open(os.path.join(SCRIPT_DIR, 'portfolio_adjustment_data.json'), 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
        
    print("Analysis complete.")

if __name__ == '__main__':
    main()

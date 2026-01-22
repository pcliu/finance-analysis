import sys
import os
import json
import pandas as pd
from datetime import datetime

# Setup SKILL_DIR
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import fetch_multiple_stocks, calculate_rsi, calculate_sma, calculate_bollinger_bands, calculate_macd, calculate_stochastic, calculate_atr
from scripts.utils import make_serializable

# Configuration
HOLDINGS_PATH = '/Users/liupengcheng/.gemini/antigravity/brain/0b2a059f-4349-4bbc-870e-77bdbcf8530d/current_holdings.json'
ETFS_CSV_PATH = '/Users/liupengcheng/Documents/Code/finance-analysis/workspace/ETFs.csv'
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    # 1. Load Holdings
    with open(HOLDINGS_PATH, 'r') as f:
        holdings = json.load(f)
    
    holding_codes = [str(h['code']) for h in holdings]
    
    # 2. Load Candidates
    candidates = []
    if os.path.exists(ETFS_CSV_PATH):
        try:
            df_etfs = pd.read_csv(ETFS_CSV_PATH)
            # Normalize column names if needed
            df_etfs.columns = [c.strip() for c in df_etfs.columns]
            
            for _, row in df_etfs.iterrows():
                code = str(row['代码']).strip()
                name = row['ETF 名称']
                if code not in holding_codes:
                    candidates.append({'code': code, 'name': name})
        except Exception as e:
            print(f"Error reading ETFs.csv: {e}")
    
    candidate_codes = [c['code'] for c in candidates]
    all_codes = list(set(holding_codes + candidate_codes))
    
    print(f"Fetching data for {len(all_codes)} tickers...")
    
    # 3. Fetch Data (6mo is enough for indicators)
    try:
        data_map = fetch_multiple_stocks(all_codes, period='6mo')
    except Exception as e:
        print(f"Error fetching stocks: {e}")
        return

    results = {
        'timestamp': datetime.now().isoformat(),
        'holdings': {},
        'candidates': {}
    }
    
    # 4. Calculate Indicators
    for code in all_codes:
        if code not in data_map or data_map[code].empty:
            print(f"Warning: No data for {code}")
            continue
            
        df = data_map[code]
        if len(df) < 30:
            print(f"Warning: Insufficient data for {code}")
            continue

        try:
            # Basic Indicators
            rsi6 = calculate_rsi(df, window=6).iloc[-1]['RSI']
            rsi14 = calculate_rsi(df, window=14).iloc[-1]['RSI']
            sma20 = calculate_sma(df, window=20).iloc[-1]['SMA']
            bb = calculate_bollinger_bands(df, window=20, num_std=2).iloc[-1]
            
            # Advanced Indicators
            macd = calculate_macd(df).iloc[-1]
            stoch = calculate_stochastic(df).iloc[-1]
            atr = calculate_atr(df, window=14).iloc[-1]['ATR']
            
            # Price & Returns
            close_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            pct_change = (close_price - prev_close) / prev_close * 100
            
            # Volume Analysis
            vol_sma5 = df['Volume'].rolling(5).mean().iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / vol_sma5 if vol_sma5 > 0 else 1.0
            
            # 20-day return
            price_20d_ago = df['Close'].iloc[-21] if len(df) > 20 else df['Close'].iloc[0]
            ret_20d = (close_price - price_20d_ago) / price_20d_ago * 100
            
            # 5-day return (momentum)
            price_5d_ago = df['Close'].iloc[-6] if len(df) > 5 else df['Close'].iloc[0]
            ret_5d = (close_price - price_5d_ago) / price_5d_ago * 100

            metric = {
                'price': close_price,
                'pct_change': pct_change,
                'rsi6': rsi6,
                'rsi14': rsi14,
                'sma20': sma20,
                'bb_upper': bb['Upper'],
                'bb_lower': bb['Lower'],
                'bb_pct_b': (close_price - bb['Lower']) / (bb['Upper'] - bb['Lower']) if (bb['Upper'] - bb['Lower']) != 0 else 0.5,
                'macd': macd['MACD'],
                'macd_signal': macd['Signal'],
                'macd_hist': macd['Histogram'],
                'kdj_k': stoch['K'],
                'kdj_d': stoch['D'],
                'atr': atr,
                'vol_ratio': vol_ratio,
                'ret_20d': ret_20d,
                'ret_5d': ret_5d
            }
            
            if code in holding_codes:
                h_info = next(h for h in holdings if str(h['code']) == code)
                # Avoid overwriting calculated fields if they exist in h_info (unlikely, but safe)
                # But h_info has 'price' and 'market_value' from user input, we prefer real-time 'price' 
                # actually let's keep user input meta but use calculated price
                metric.update({k:v for k,v in h_info.items() if k not in ['price']}) # Keep calculated price
                results['holdings'][code] = metric
            else:
                c_info = next((c for c in candidates if c['code'] == code), {'name': 'Unknown'})
                metric.update(c_info)
                results['candidates'][code] = metric
                
        except Exception as e:
            print(f"Error calculating metrics for {code}: {e}")

    # 5. Save Results
    output_path = os.path.join(OUTPUT_DIR, 'portfolio_adjustment_data.json')
    with open(output_path, 'w') as f:
        json.dump(make_serializable(results), f, indent=4, ensure_ascii=False)
    
    print(f"Analysis complete. Data saved to {output_path}")

if __name__ == "__main__":
    main()

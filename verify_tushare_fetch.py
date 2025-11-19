import sys
import os
import pandas as pd

# Add the skill directory to Python path
sys.path.append('quantitative-trading-skills/quantitative-trading')

from api.data_fetcher import fetch_stock_data

def verify_fetch(ticker, expected_asset_type):
    print(f"\nTesting fetch for {ticker} (Expected: {expected_asset_type})...")
    try:
        # Force tushare provider
        data = fetch_stock_data(ticker, period='1mo', provider='tushare')
        
        if data is not None and not data.empty:
            print(f"✅ Success! Fetched {len(data)} rows.")
            print(data.tail())
            return True
        else:
            print(f"❌ Failed! No data returned.")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Tushare Fetch Verification...")
    
    # Test cases
    results = []
    
    # 1. Stock (Equity) - Moutai
    results.append(verify_fetch('600519.SH', 'E'))
    
    # 2. Index - SSE Composite
    results.append(verify_fetch('000001.SH', 'I'))
    
    # 3. Fund (ETF) - Huatai 300 ETF
    results.append(verify_fetch('510300.SH', 'FD'))
    
    # 4. Stock (Equity) - Ping An Bank
    results.append(verify_fetch('000001.SZ', 'E'))
    
    if all(results):
        print("\n✅ All verification tests passed!")
    else:
        print("\n❌ Some verification tests failed.")

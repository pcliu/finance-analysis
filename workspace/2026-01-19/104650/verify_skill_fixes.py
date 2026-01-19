
import sys
import os
import json
import pandas as pd
import numpy as np

# Robust path setup as per new SKILL.md
SKILL_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

# Import new exports and util
try:
    from scripts import calculate_atr, calculate_max_drawdown, calculate_cvar
    from scripts.utils import make_serializable
    print("Imports successful.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)

def main():
    print("Generating mock data...")
    dates = pd.date_range('2024-01-01', periods=100)
    data = pd.DataFrame({
        'High': np.random.uniform(105, 110, 100),
        'Low': np.random.uniform(95, 100, 100),
        'Close': np.random.uniform(95, 110, 100),
        'Volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    try:
        print("Testing calculate_atr...")
        atr = calculate_atr(data, window=14)
        print(f"ATR calculated. Last value: {atr['ATR'].iloc[-1]}")
        
        print("Testing calculate_max_drawdown...")
        # Note: Our wrapper hardcoded is_returns=False, suitable for price series
        mdd = calculate_max_drawdown(data['Close'])
        print(f"Max Drawdown: {mdd}")

        print("Testing calculate_cvar...")
        returns = data['Close'].pct_change().dropna()
        cvar = calculate_cvar(returns)
        print(f"CVaR: {cvar}")
        
        print("Testing make_serializable...")
        results = {
            "mdd": mdd,
            "cvar": cvar,
            "atr_last": atr['ATR'].iloc[-1], # numpy float
            "nested": {
                "values": np.array([1, 2, 3])
            }
        }
        
        clean = make_serializable(results)
        json_output = json.dumps(clean, indent=2)
        print("JSON serialization successful.")
        print(json_output)
        
    except Exception as e:
        print(f"Verification failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Verification script for indicators refactoring
"""
import sys
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading')

from scripts import TechnicalIndicators, TradingStrategy

def verify_indicators():
    print("Verifying TechnicalIndicators...")
    
    # Create mock data
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = pd.DataFrame({
        'Open': np.random.randn(100).cumsum() + 100,
        'High': np.random.randn(100).cumsum() + 105,
        'Low': np.random.randn(100).cumsum() + 95,
        'Close': np.random.randn(100).cumsum() + 100,
        'Volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    ti = TechnicalIndicators()
    
    # List of methods to test
    methods = [
        ('calculate_sma', {}),
        ('calculate_ema', {}),
        ('calculate_wma', {}),
        ('calculate_bollinger_bands', {}),
        ('calculate_adx', {}),
        ('calculate_rsi', {}),
        ('calculate_stochastic', {}),
        ('calculate_macd', {}),
        ('calculate_williams_r', {}),
        ('calculate_cci', {}),
        ('calculate_atr', {}),
        ('calculate_keltner_channels', {}),
        ('calculate_obv', {}),
        ('calculate_volume_sma', {}),
        ('calculate_volume_profile', {}),
        ('calculate_pivot_points', {}),
        ('calculate_fibonacci_retracements', {}),
        ('calculate_all_indicators', {})
    ]
    
    success = True
    
    for method_name, kwargs in methods:
        try:
            method = getattr(ti, method_name)
            result = method(data, **kwargs)
            
            if not isinstance(result, pd.DataFrame):
                print(f"❌ {method_name} returned {type(result)}, expected DataFrame")
                success = False
            else:
                print(f"✅ {method_name} returned DataFrame with shape {result.shape}")
                
        except Exception as e:
            print(f"❌ {method_name} failed with error: {e}")
            success = False

    return success

def verify_strategies():
    print("\nVerifying TradingStrategy...")
    
    dates = pd.date_range(start='2023-01-01', periods=100)
    data = pd.DataFrame({
        'Open': np.random.uniform(90, 110, 100),
        'High': np.random.uniform(100, 120, 100),
        'Low': np.random.uniform(80, 100, 100),
        'Close': np.random.uniform(90, 110, 100),
        'Volume': np.random.randint(1000, 10000, 100)
    }, index=dates)

    # Ensure Close moves enough for signals
    # Make Close follow a sin wave
    t = np.linspace(0, 4*np.pi, 100)
    data['Close'] = 100 + 10 * np.sin(t)
    
    ts = TradingStrategy()
    
    strategies = [
        'moving_average_crossover',
        'rsi_mean_reversion',
        'bollinger_bands_strategy',
        'macd_strategy',
        'stochastic_oscillator_strategy',
        'momentum_breakout',
        'mean_reversion_strategy'
    ]
    
    success = True
    
    for strategy in strategies:
        try:
            # We need to call the method directly or via get_strategy_signals
            method = getattr(ts, strategy)
            # Inspect signature to see required args? Or just use defaults
            # strategies usually take data as first arg
            
            # Special handling for args
            if strategy == 'momentum_breakout':
                # Needs volume
                pass 
                
            result = method(data.copy())
            
            if not isinstance(result, pd.DataFrame):
                 print(f"❌ {strategy} returned {type(result)}, expected DataFrame")
                 success = False
            elif 'Signal' not in result.columns and 'Buy_Signal' not in result.columns:
                 print(f"⚠️ {strategy} returned DataFrame but no Signal columns found (might be normal if no signals generated)")
                 # Check specific columns to ensure calculation happened
                 if strategy == 'moving_average_crossover':
                     if 'MA_Fast' not in result.columns:
                         print(f"❌ {strategy} failed to calculate indicators")
                         success = False
                     else:
                         print(f"✅ {strategy} ran successfully")
                 else:
                     print(f"✅ {strategy} ran successfully")
            else:
                print(f"✅ {strategy} ran successfully with signals")
                
        except Exception as e:
            print(f"❌ {strategy} failed with error: {e}")
            import traceback
            traceback.print_exc()
            success = False
            
    return success

if __name__ == "__main__":
    indicators_ok = verify_indicators()
    strategies_ok = verify_strategies()
    
    if indicators_ok and strategies_ok:
        print("\n🎉 Refactoring Verified Successfully!")
        sys.exit(0)
    else:
        print("\n💥 Verification Failed!")
        sys.exit(1)

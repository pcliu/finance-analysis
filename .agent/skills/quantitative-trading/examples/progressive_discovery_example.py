#!/usr/bin/env python3
"""
Progressive Discovery Example

This demonstrates how models can discover and use tools progressively
by exploring the filesystem, rather than loading all definitions upfront.
"""

import os
import sys

def discover_api_modules():
    """
    Simulate how a model would discover available API modules
    by exploring the filesystem.
    """
    api_dir = os.path.join(os.path.dirname(__file__), '..', 'api')
    
    print("Discovering API modules...")
    print("=" * 50)
    
    # List top-level modules
    modules = []
    for item in os.listdir(api_dir):
        item_path = os.path.join(api_dir, item)
        if os.path.isdir(item_path) and not item.startswith('__'):
            modules.append(item)
            print(f"\n📁 Module: {item}")
            
            # List functions in each module
            init_file = os.path.join(item_path, '__init__.py')
            if os.path.exists(init_file):
                with open(init_file, 'r') as f:
                    content = f.read()
                    # Extract exported functions
                    if '__all__' in content:
                        print(f"   Available functions:")
                        for line in content.split('\n'):
                            if line.strip().startswith("'") or line.strip().startswith('"'):
                                func_name = line.strip().strip("'\"")
                                if func_name and not func_name.startswith('_'):
                                    print(f"     - {func_name}")
    
    return modules

def demonstrate_progressive_loading():
    """
    Demonstrate loading only what you need.
    """
    print("\n" + "=" * 50)
    print("Progressive Loading Example")
    print("=" * 50)
    
    # Step 1: Discover available modules
    modules = discover_api_modules()
    
    # Step 2: Load only what you need for the task
    print("\n📋 Task: Analyze a stock's RSI")
    print("   → Only need: data_fetcher and indicators modules")
    
    # Import only needed functions
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
    from api.data_fetcher import fetch_stock_data
    from api.indicators import calculate_rsi
    
    print("   ✓ Loaded: fetch_stock_data, calculate_rsi")
    print("   ✗ Skipped: strategies, backtester, portfolio, risk modules")
    
    # Step 3: Use the functions
    print("\n   Executing analysis...")
    data = fetch_stock_data('AAPL', period='1y')
    if data is not None:
        rsi = calculate_rsi(data)
        current_rsi = rsi.iloc[-1]
        print(f"   Result: Current RSI = {current_rsi:.2f}")
    
    print("\n💡 Benefit: Only loaded 2 functions instead of all 20+ functions")
    print("   Context window saved: ~95%")

if __name__ == "__main__":
    demonstrate_progressive_loading()

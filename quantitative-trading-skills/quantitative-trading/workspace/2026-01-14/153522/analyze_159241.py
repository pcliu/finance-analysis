#!/usr/bin/env python3
"""
Analysis script for 159241 (Aerospace/Defense ETF or similar)
Saved to: workspace/2026-01-14/153522/analyze_159241.py
"""

import sys
import os
import json
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, TechnicalIndicators

# Setup output directory
output_dir = "/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading/workspace/2026-01-14/153522"
os.makedirs(output_dir, exist_ok=True)

def generate_report(ticker, data, indicators_df, output_dir):
    """Generate analysis report based on template."""
    
    last_close = data['Close'].iloc[-1]
    last_date = data.index[-1].strftime('%Y-%m-%d')
    
    # Extract key indicators from the merged DataFrame
    # Note: indicators_df is already joined to data or is the source
    # The merged DF has columns like RSI, MACD, etc.
    
    rsi = indicators_df['RSI'].iloc[-1] if 'RSI' in indicators_df else float('nan')
    macd = indicators_df['MACD_MACD'].iloc[-1] if 'MACD_MACD' in indicators_df else float('nan')
    
    # Determine trend (simple logic for now)
    trend = "中性"
    if rsi > 70: trend = "超买"
    elif rsi < 30: trend = "超卖"
    
    # Construct details for all indicators
    indicators_list = []
    # We'll list some key columns to avoid cluttering with OHLC
    key_cols = [c for c in indicators_df.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
    
    for col in key_cols:
        val = indicators_df[col].iloc[-1]
        indicators_list.append(f"- **{col}**: {val:.4f}")
    
    indicators_md = "\n".join(indicators_list)

    report_content = f"""# 投资分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. 市场概况与持仓分析

针对 {ticker} ({last_date}) 的全面技术指标分析。

**现有持仓诊断：**

*   **{ticker}**：当前价格 {last_close:.2f}。
    *   **RSI (14)**: {rsi:.2f} - {trend}
    *   **MACD**: {macd:.4f}
    *   **趋势状态**: 依据技术指标自动生成的初步判断。

## 2. 关注标的分析

本次重点分析 {ticker} 的全套技术指标。

### 详细指标一览 ({last_date})
{indicators_md}

## 3. 历史策略复盘（最近5次报告）

(此处为单次分析，无历史复盘数据)

## 4. 具体操作建议

基于当前指标的自动化建议（仅供参考）：
*   RSI: {rsi:.2f}
*   MACD: {macd:.4f}

## 5. 调整后展望

*   **风险提示**: 请结合基本面和市场情绪综合判断。

## 6. 生成文件
- `analyze_159241.py` - 分析脚本
- `indicators_159241.csv` - 包含所有指标的数据
"""
    
    with open(f"{output_dir}/analysis_report.md", "w") as f:
        f.write(report_content)
    
    print(f"Report generated: {output_dir}/analysis_report.md")

def main():
    ticker = '159241.SZ' # Assumption based on 15xxxx usually being SZ
    print(f"Fetching data for {ticker}...")
    
    # Fetch data (using 1 year to ensure enough data for indicators)
    try:
        data = fetch_stock_data(ticker, period='1y')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    if data is None or data.empty:
        print("Failed to fetch data.")
        return

    print(f"Data fetched: {len(data)} rows.")

    # Calculate ALL indicators
    print("Calculating all technical indicators...")
    ti = TechnicalIndicators()
    try:
        # returns a DataFrame now
        indicators_df = ti.calculate_all_indicators(data)
        
        # Merge indicators into main dataframe
        # Note: calculate_all_indicators returns ONLY indicators, so we join
        final_df = data.join(indicators_df)
            
    except Exception as e:
        print(f"Error calculating indicators: {e}")
        import traceback
        traceback.print_exc()
        return

    # Save to CSV
    csv_path = f"{output_dir}/indicators_159241.csv"
    final_df.to_csv(csv_path)
    print(f"Indicators saved to {csv_path}")
    
    # Print latest values of some key columns
    print("\nLatest Indicator Values:")
    latest = final_df.iloc[-1]
    for col in final_df.columns:
        if col not in ['Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']:
            print(f"{col}: {latest[col]}")

    # Generate Report
    generate_report(ticker, data, final_df, output_dir)

if __name__ == "__main__":
    main()

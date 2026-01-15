import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to sys.path to import scripts
# Current file is in workspace/2026-01-15/092833/
# Project root is three levels up from the workspace/YYYY-MM-DD/HHMMSS directory? 
# No, Skill root is /Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading
# Let's find the absolute path.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

from scripts import (
    fetch_stock_data, 
    TechnicalIndicators, 
    fetch_multiple_stocks
)

def analyze_slv():
    ticker = 'SLV'
    print(f"Starting technical analysis for {ticker}...")
    
    # 1. Fetch Data
    # Fetch 1 year of data to have enough for 200-day SMA
    data = fetch_stock_data(ticker, period='1y')
    if data is None or data.empty:
        print(f"Error: Could not fetch data for {ticker}")
        return

    # 2. Calculate Indicators
    ti = TechnicalIndicators()
    indicators_df = ti.calculate_all_indicators(data)
    
    # Combined data
    full_df = data.join(indicators_df)
    
    # Get the latest values
    latest = full_df.iloc[-1]
    
    # Calculate some additional metrics for the report
    price = latest['Close']
    rsi = latest['RSI']
    macd = latest['MACD_MACD']
    signal = latest['MACD_Signal']
    hist = latest['MACD_Histogram']
    sma20 = latest['SMA_20']
    sma50 = latest['SMA_50']
    bb_upper = latest['BB_Upper']
    bb_middle = latest['BB_Middle']
    bb_lower = latest['BB_Lower']
    cci = latest['CCI']
    atr = latest['ATR']
    
    # Annualized Volatility (Rolling 20 days)
    returns = data['Close'].pct_change().dropna()
    volatility = returns.tail(20).std() * np.sqrt(252) * 100
    
    # Trend Analysis
    trend_desc = ""
    if price > sma20 > sma50:
        trend_desc = "短期均线 > 中期均线，且价格处于均线上方，典型的多头排列，强势上升趋势。"
    elif price < sma20 < sma50:
        trend_desc = "短期均线 < 中期均线，且价格处于均线下方，典型的空头排列，弱势下跌趋势。"
    else:
        trend_desc = "均线交织，价格在均线附近震荡，趋势处于调整或盘整阶段。"

    # RSI Interpretation
    rsi_desc = ""
    if rsi >= 70:
        rsi_desc = f"RSI 为 {rsi:.2f}，进入超买区间，需警惕短期回调风险。"
    elif rsi <= 30:
        rsi_desc = f"RSI 为 {rsi:.2f}，进入超卖区间，可能存在反弹机会。"
    else:
        rsi_desc = f"RSI 为 {rsi:.2f}，处于中性区域，动能平稳。"

    # MACD Interpretation
    macd_desc = ""
    if macd > signal:
        macd_desc = "MACD 位于信号线上方（金叉），且柱状图为正，上升动能保持中。"
    else:
        macd_desc = "MACD 位于信号线下方（死叉），下降压力增大，需注意观望。"

    # BB Interpretation
    bb_desc = ""
    percent_b = (price - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0
    if percent_b > 0.8:
        bb_desc = "价格运行在布林带上轨附近，显示市场情绪亢奋，处于强势区间。"
    elif percent_b < 0.2:
        bb_desc = "价格运行在布林带下轨附近，显示市场抛压较重，处于弱势区间。"
    else:
        bb_desc = "价格运行在布林带通道内，波动相对平稳。"

    # Prepare Report
    report_content = f"""# {ticker} 技术指标分析报告
**分析日期**: {datetime.now().strftime('%Y-%m-%d')} (数据截止 {data.index[-1].strftime('%Y-%m-%d')})

## 1. 核心指标状态
*   **当前价格**: {price:.2f}
*   **RSI (14)**: {rsi:.2f}
    *   *解读*: {rsi_desc}
*   **MACD**: {macd:.4f} (DIF)
    *   **Signal**: {signal:.4f} (DEA)
    *   **Histogram**: {hist:.4f}
    *   *解读*: {macd_desc}

## 2. 趋势与通道
*   **均线系统**:
    *   **SMA 20 (月线)**: {sma20:.2f}
    *   **SMA 50 (季线)**: {sma50:.2f}
    *   *状态*: {trend_desc}
*   **布林带 (Bollinger Bands)**:
    *   **上轨**: {bb_upper:.2f}
    *   **中轨**: {bb_middle:.2f}
    *   **下轨**: {bb_lower:.2f}
    *   *状态*: {bb_desc}
*   **CCI**: {cci:.2f}
    *   *解读*: {"CCI 大于 100，处于强势状态" if cci > 100 else "CCI 小于 -100，处于弱势状态" if cci < -100 else "CCI 处于常态区间"}。

## 3. 波动性
*   **ATR (14)**: {atr:.2f}
*   **Volatility**: {volatility:.2f}% (20日年化波动率)

## 4. 📊 生成文件
您可以在以下位置找到详细数据：

*   **指标数据 (CSV)**: `technical_analysis_{ticker}_data.csv`
*   **分析脚本**: `technical_analysis_{ticker}.py`
*   **JSON 数据**: `technical_analysis_{ticker}_data.json`
"""

    # Save outputs to SCRIPT_DIR
    report_path = os.path.join(SCRIPT_DIR, f'technical_analysis_{ticker}_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    csv_path = os.path.join(SCRIPT_DIR, f'technical_analysis_{ticker}_data.csv')
    full_df.to_csv(csv_path)
    
    data_output = {
        'ticker': ticker,
        'last_price': float(price),
        'indicators': {
            'rsi': float(rsi),
            'macd': float(macd),
            'macd_signal': float(signal),
            'macd_hist': float(hist),
            'sma20': float(sma20),
            'sma50': float(sma50),
            'bb_upper': float(bb_upper),
            'bb_middle': float(bb_middle),
            'bb_lower': float(bb_lower),
            'cci': float(cci),
            'atr': float(atr),
            'volatility': float(volatility)
        },
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'data_cutoff': data.index[-1].strftime('%Y-%m-%d')
    }
    
    json_path = os.path.join(SCRIPT_DIR, f'technical_analysis_{ticker}_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_output, f, indent=4)

    print(f"Analysis complete. Results saved in {SCRIPT_DIR}")

if __name__ == "__main__":
    analyze_slv()

import os
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add the project root to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, '..', '..', '..'))
sys.path.append(PROJECT_ROOT)

from scripts import (
    fetch_stock_data, 
    TradingStrategies, 
    TechnicalIndicators
)

def analyze_slv_signals():
    ticker = 'SLV'
    print(f"Starting strategy signal analysis for {ticker}...")
    
    # 1. Fetch Data
    data = fetch_stock_data(ticker, period='1y')
    if data is None or data.empty:
        print(f"Error: Could not fetch data for {ticker}")
        return

    # 2. Generate Signals
    ts = TradingStrategies()
    ti = TechnicalIndicators()
    
    # Get multi-strategy signals
    signals_df = ts.multi_strategy_signals(data)
    
    # Additionally get the raw indicator values for the report
    all_indicators = ti.calculate_all_indicators(data)
    full_df = signals_df.join(all_indicators, rsuffix='_raw')
    
    # Latest data point
    latest = full_df.iloc[-1]
    price = latest['Close']
    
    # Strategy signals (1: Buy, -1: Sell, 0: None)
    # Mapping columns from multi_strategy_signals
    # Columns expected: MA_Signal, RSI_Signal, MACD_Signal, BB_Signal, Stoch_Signal, Momentum_Signal, MeanRev_Signal, Consensus_Signal, Final_Signal
    
    def get_signal_str(val):
        if val > 0: return "BUY"
        if val < 0: return "SELL"
        return "NONE"

    ma_signal = get_signal_str(latest.get('MA_Signal', 0))
    macd_signal = get_signal_str(latest.get('MACD_Signal', 0))
    rsi_signal = get_signal_str(latest.get('RSI_Signal', 0))
    bb_signal = get_signal_str(latest.get('BB_Signal', 0))
    stoch_signal = get_signal_str(latest.get('Stoch_Signal', 0))
    mom_signal = get_signal_str(latest.get('Momentum_Signal', 0))
    mr_signal = get_signal_str(latest.get('MeanRev_Signal', 0))
    
    consensus_score = latest.get('Consensus_Signal', 0)
    final_rating = "BUY" if consensus_score > 0.3 else "SELL" if consensus_score < -0.3 else "HOLD"

    # Recent signals (last 5-10 days)
    recent_signals = []
    last_10 = full_df.tail(10)
    
    # Define which columns represent specific buy/sell triggers in the underlying strategies
    # For simplicity, we'll check if any signal column changed or is non-zero in the last 5 days
    check_days = 5
    for i in range(1, check_days + 1):
        idx = -i
        day_data = full_df.iloc[idx]
        day_date = full_df.index[idx].strftime('%Y-%m-%d')
        
        # Check for specific buy/sell signals
        if day_data.get('Final_Signal', 0) != 0:
            action = "BUY" if day_data['Final_Signal'] > 0 else "SELL"
            recent_signals.append(f"*   **{day_date}**: 综合信号评估为 **{action}**")
            
    if not recent_signals:
        recent_signals.append("*   近期无重大策略转向信号。")

    # Interpretations for the table
    ma_desc = "短期均线高于长期均线" if latest.get('MA_Fast', 0) > latest.get('MA_Slow', 0) else "短期均线低于长期均线"
    macd_desc = "DIF 上穿 DEA" if latest.get('MACD_MACD', 0) > latest.get('MACD_Signal', 0) else "DIF 下穿 DEA"
    rsi_desc = "RSI 进入超买区 (>70)" if latest.get('RSI', 0) > 70 else "RSI 处于正常/超卖区间"
    bb_desc = "触及或突破上轨" if price >= latest.get('BB_Upper', 9999) else "触及或跌破下轨" if price <= latest.get('BB_Lower', 0) else "在通道内运行"

    # Prepare Report
    report_content = f"""# {ticker} 策略信号分析报告
**分析日期**: {datetime.now().strftime('%Y-%m-%d')} (数据截止 {data.index[-1].strftime('%Y-%m-%d')})

## 1. 综合信号建议
*   **当前价格**: {price:.2f}
*   **综合评级**: **{final_rating}** (Consensus Score: {consensus_score:.2f})
    *   *解读*: 综合得分为 {consensus_score:.2f}。{"多数策略看多，短线动能强劲。" if consensus_score > 0 else "策略间存在分歧，或多数呈现看空信号。" if consensus_score < 0 else "策略信号相互抵消，市场趋势不明朗。"}

## 2. 策略详细表现
| 策略名称                      | 信号状态        | 信号日期 | 描述                       |
| :---------------------------- | :-------------- | :------- | :------------------------- |
| **均线交叉 (MA Crossover)**   | {ma_signal} | {data.index[-1].strftime('%Y-%m-%d')} | {ma_desc} |
| **MACD 策略**                 | {macd_signal} | {data.index[-1].strftime('%Y-%m-%d')} | {macd_desc} |
| **RSI 均值回归**              | {rsi_signal} | {data.index[-1].strftime('%Y-%m-%d')} | {rsi_desc} |
| **布林带突破**                | {bb_signal} | {data.index[-1].strftime('%Y-%m-%d')} | {bb_desc} |
| **动量突破**                  | {mom_signal} | {data.index[-1].strftime('%Y-%m-%d')} | 价格显著上涨且伴随成交量 |
| **随机指标 (Stochastic)**     | {stoch_signal} | {data.index[-1].strftime('%Y-%m-%d')} | K线与D线交叉状态 |
| **均值回归 (Mean Reversion)** | {mr_signal} | {data.index[-1].strftime('%Y-%m-%d')} | 价格对均线的偏离程度 |

## 3. 核心指标概览
*   **RSI (14)**: {latest.get('RSI', 0):.2f}
*   **MACD**: {latest.get('MACD_MACD', 0):.4f} (Signal: {latest.get('MACD_Signal', 0):.4f})
*   **市场趋势**: {"多头排列" if latest.get('SMA_20', 0) > latest.get('SMA_50', 0) else "空头排列"}

## 4. 近期信号追踪
{chr(10).join(recent_signals)}

## 5. 📊 生成文件
*   **完整报告**: `strategy_signal_{ticker}_report.md`
*   **信号数据**: `strategy_signal_{ticker}_data.json`
*   **分析脚本**: `strategy_signal_{ticker}.py`
"""

    # Save outputs
    report_path = os.path.join(SCRIPT_DIR, f'strategy_signal_{ticker}_report.md')
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Save CSV for reference
    csv_path = os.path.join(SCRIPT_DIR, f'strategy_signal_{ticker}_data.csv')
    full_df.to_csv(csv_path)
    
    # Save JSON for analysis
    data_output = {
        'ticker': ticker,
        'last_price': float(price),
        'signals': {
            'ma': ma_signal,
            'macd': macd_signal,
            'rsi': rsi_signal,
            'bb': bb_signal,
            'momentum': mom_signal,
            'consensus_score': float(consensus_score),
            'final_rating': final_rating
        },
        'analysis_date': datetime.now().strftime('%Y-%m-%d'),
        'data_cutoff': data.index[-1].strftime('%Y-%m-%d')
    }
    
    json_path = os.path.join(SCRIPT_DIR, f'strategy_signal_{ticker}_data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_output, f, indent=4)

    print(f"Signal analysis complete. Results saved in {SCRIPT_DIR}")

if __name__ == "__main__":
    analyze_slv_signals()

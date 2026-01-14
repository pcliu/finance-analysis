#!/usr/bin/env python3
import sys
import os
import json
import pandas as pd
import numpy as np
from datetime import datetime

# Add skill path to sys.path
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import fetch_stock_data, TradingStrategies, TechnicalIndicators

def analyze_ticker(ticker):
    # Create output directory
    now = datetime.now()
    output_dir = f"/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading/workspace/{now.strftime('%Y-%m-%d')}/{now.strftime('%H%M%S')}"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Fetching data for {ticker}...")
    try:
        data = fetch_stock_data(ticker, period='1y', market='cn')
    except Exception as e:
        print(f"Error fetching data: {e}")
        return
        
    if data is None or data.empty:
        print(f"No data found for {ticker}")
        return

    ts = TradingStrategies()
    ti = TechnicalIndicators()
    
    print(f"Generating signals...")
    signals_df = ts.multi_strategy_signals(data)
    
    # Calculate indicators needed for report explicitly
    rsi_df = ti.calculate_rsi(data)
    macd_dict = ti.calculate_macd(data)
    bb_dict = ti.calculate_bollinger_bands(data)
    ma20 = ti.calculate_sma(data, window=20)
    ma50 = ti.calculate_sma(data, window=50)
    
    latest_idx = signals_df.index[-1]
    latest = signals_df.iloc[-1]
    
    analysis_results = {
        "ticker": ticker,
        "date": latest_idx.strftime('%Y-%m-%d'),
        "price": float(data['Close'].iloc[-1]),
        "signals": {},
        "indicators": {}
    }
    
    # MA Crossover
    ma_data = ts.moving_average_crossover(data.copy())
    last_ma = ma_data.iloc[-1]
    analysis_results["signals"]["ma_crossover"] = {
        "status": "BUY" if last_ma['Buy_Signal'] else "SELL" if last_ma['Sell_Signal'] else "NONE",
        "description": f"Fast MA: {last_ma['MA_Fast']:.2f}, Slow MA: {last_ma['MA_Slow']:.2f}"
    }
    
    # MACD
    macd_data = ts.macd_strategy(data.copy())
    last_macd = macd_data.iloc[-1]
    analysis_results["signals"]["macd"] = {
        "status": "BUY" if last_macd['Buy_Signal'] else "SELL" if last_macd['Sell_Signal'] else "NONE",
        "description": f"MACD: {last_macd['MACD']:.4f}, Signal: {last_macd['MACD_Signal']:.4f}"
    }
    
    # RSI
    rsi_data = ts.rsi_mean_reversion(data.copy())
    last_rsi = rsi_data.iloc[-1]
    analysis_results["signals"]["rsi"] = {
        "status": "BUY" if last_rsi['Buy_Signal'] else "SELL" if last_rsi['Sell_Signal'] else "NONE",
        "description": f"RSI: {last_rsi['RSI']:.2f}"
    }
    
    # Bollinger Bands
    bb_data = ts.bollinger_bands_strategy(data.copy())
    last_bb = bb_data.iloc[-1]
    analysis_results["signals"]["bollinger"] = {
        "status": "BUY" if last_bb['Buy_Signal'] else "SELL" if last_bb['Sell_Signal'] else "NONE",
        "description": f"Price: {last_bb['Close']:.2f}, Lower: {last_bb['BB_Lower']:.2f}, Upper: {last_bb['BB_Upper']:.2f}"
    }
    
    # momentum
    mom_data = ts.momentum_breakout(data.copy())
    last_mom = mom_data.iloc[-1]
    analysis_results["signals"]["momentum"] = {
        "status": "BUY" if last_mom['Buy_Signal'] else "SELL" if last_mom['Sell_Signal'] else "NONE",
        "description": "Momentum Breakout" if last_mom['Buy_Signal'] or last_mom['Sell_Signal'] else "No Breakout"
    }
    
    # Stochastic
    stoch_data = ts.stochastic_oscillator_strategy(data.copy())
    last_stoch = stoch_data.iloc[-1]
    analysis_results["signals"]["stochastic"] = {
        "status": "BUY" if last_stoch['Buy_Signal'] else "SELL" if last_stoch['Sell_Signal'] else "NONE",
        "description": f"K: {last_stoch['Stoch_K']:.2f}, D: {last_stoch['Stoch_D']:.2f}"
    }

    # Mean Reversion
    mr_data = ts.mean_reversion_strategy(data.copy())
    last_mr = mr_data.iloc[-1]
    analysis_results["signals"]["mean_reversion"] = {
        "status": "BUY" if last_mr['Buy_Signal'] else "SELL" if last_mr['Sell_Signal'] else "NONE",
        "description": f"Z-Score: {last_mr['Z_Score']:.2f}"
    }

    # Consensus Score
    consensus_score = float(latest['Consensus_Signal'])
    analysis_results["consensus_score"] = consensus_score
    analysis_results["rating"] = "BUY" if consensus_score > 0.5 else "SELL" if consensus_score < -0.5 else "HOLD"
    
    # Core Indicators
    analysis_results["indicators"]["rsi"] = float(rsi_df['RSI'].iloc[-1])
    analysis_results["indicators"]["macd"] = float(macd_dict['MACD'].iloc[-1])
    analysis_results["indicators"]["macd_signal"] = float(macd_dict['Signal'].iloc[-1])
    
    # Market Trend
    last_price = data['Close'].iloc[-1]
    l_ma20 = ma20['SMA'].iloc[-1]
    l_ma50 = ma50['SMA'].iloc[-1]
    
    if last_price > l_ma20 and l_ma20 > l_ma50:
        trend = "多头排列 (Bullish)"
    elif last_price < l_ma20 and l_ma20 < l_ma50:
        trend = "空头排列 (Bearish)"
    else:
        trend = "震荡 (Sideways)"
    analysis_results["trend"] = trend

    # Recent Signals (last 5 days)
    recent_signals = []
    for i in range(1, 6):
        day_idx = -i
        day_data = signals_df.iloc[day_idx]
        day_date = signals_df.index[day_idx].strftime('%Y-%m-%d')
        day_sig_list = []
        if day_data.get('MA_Signal') != 0: day_sig_list.append(f"MA Crossover ({'BUY' if day_data['MA_Signal'] > 0 else 'SELL'})")
        if day_data.get('RSI_Signal') != 0: day_sig_list.append(f"RSI ({'BUY' if day_data['RSI_Signal'] > 0 else 'SELL'})")
        if day_data.get('MACD_Signal') != 0: day_sig_list.append(f"MACD ({'BUY' if day_data['MACD_Signal'] > 0 else 'SELL'})")
        if day_data.get('BB_Signal') != 0: day_sig_list.append(f"Bollinger ({'BUY' if day_data['BB_Signal'] > 0 else 'SELL'})")
        if day_sig_list:
            recent_signals.append(f"{day_date}: {', '.join(day_sig_list)}")
            
    analysis_results["recent_signals"] = recent_signals

    # Save to JSON
    with open(f"{output_dir}/analysis_result.json", "w") as f:
        json.dump(analysis_results, f, indent=4)
        
    recent_signals_text = "".join([f"*   {s}\n" for s in analysis_results['recent_signals']]) if analysis_results['recent_signals'] else "近期（5日内）未触发新信号。"
    
    # Generate Report
    report_content = f"""# {ticker} 策略信号分析报告
**分析日期**: {datetime.now().strftime('%Y-%m-%d')} (数据截止 {analysis_results['date']})

## 1. 综合信号建议
*   **当前价格**: {analysis_results['price']:.3f}
*   **综合评级**: **{analysis_results['rating']}** (Consensus Score: {analysis_results['consensus_score']:.2f})
    *   *解读*: 综合得分为 {analysis_results['consensus_score']:.2f}。{"建议积极关注买入机会。" if analysis_results['rating'] == 'BUY' else "建议谨慎对冲或减仓。" if analysis_results['rating'] == 'SELL' else "目前的信号处于均值区间，建议持仓观察。"}

## 2. 策略详细表现
| 策略名称                      | 信号状态        | 信号日期 | 描述                       |
| :---------------------------- | :-------------- | :------- | :------------------------- |
| **均线交叉 (MA Crossover)**   | {analysis_results['signals']['ma_crossover']['status']} | {analysis_results['date']} | {analysis_results['signals']['ma_crossover']['description']} |
| **MACD 策略**                 | {analysis_results['signals']['macd']['status']} | {analysis_results['date']} | {analysis_results['signals']['macd']['description']} |
| **RSI 均值回归**              | {analysis_results['signals']['rsi']['status']} | {analysis_results['date']} | {analysis_results['signals']['rsi']['description']} |
| **布林带突破**                | {analysis_results['signals']['bollinger']['status']} | {analysis_results['date']} | {analysis_results['signals']['bollinger']['description']} |
| **动量突破**                  | {analysis_results['signals']['momentum']['status']} | {analysis_results['date']} | {analysis_results['signals']['momentum']['description']} |
| **随机指标 (Stochastic)**     | {analysis_results['signals']['stochastic']['status']} | {analysis_results['date']} | {analysis_results['signals']['stochastic']['description']} |
| **均值回归 (Mean Reversion)** | {analysis_results['signals']['mean_reversion']['status']} | {analysis_results['date']} | {analysis_results['signals']['mean_reversion']['description']} |

## 3. 核心指标概览
*   **RSI (14)**: {analysis_results['indicators']['rsi']:.2f}
*   **MACD**: {analysis_results['indicators']['macd']:.4f} (Signal: {analysis_results['indicators']['macd_signal']:.4f})
*   **市场趋势**: {analysis_results['trend']}

## 4. 近期信号追踪
{recent_signals_text}

## 5. 📊 生成文件
*   **完整报告**: `{output_dir}/analysis_report.md`
*   **信号数据**: `{output_dir}/analysis_result.json`
*   **分析脚本**: `{output_dir}/analyze_{ticker}.py`
"""

    with open(f"{output_dir}/analysis_report.md", "w") as f:
        f.write(report_content)
        
    import shutil
    shutil.copy(__file__, f"{output_dir}/analyze_{ticker}.py")
    
    print(f"Analysis complete. Report saved to: {output_dir}/analysis_report.md")
    return output_dir

if __name__ == "__main__":
    ticker = "510150.SH"
    output_dir = analyze_ticker(ticker)
    print(f"OUTPUT_DIR:{output_dir}")

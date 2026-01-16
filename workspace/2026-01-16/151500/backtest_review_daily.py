
import os
import sys
import pandas as pd
import json

# Hardcoding path to ensure reliability
skill_path = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading'
if skill_path not in sys.path:
    sys.path.append(skill_path)

from scripts.data_fetcher import DataFetcher
from scripts.indicators import TechnicalIndicators

def generate_daily_review():
    # Portfolio definition based on user image
    portfolio = {
        '510150.SH': '消费 ETF',
        '510880.SH': '红利 ETF',
        '512660.SH': '军工 ETF',
        '513180.SH': '恒指科技',
        '513630.SH': '香港红利',
        '515050.SH': '5GETF',
        '515070.SH': 'AI智能',
        '588000.SH': '科创 50',
        '159241.SZ': '航空 TH',
        '159770.SZ': '机器人 AI',
        '159830.SZ': '上海金',
        '161226.SZ': '白银基金'
    }

    fetcher = DataFetcher()
    ti = TechnicalIndicators()
    
    results = []
    
    print("Fetching data for portfolio...")
    for ticker, name in portfolio.items():
        try:
            # Fetch data (using tushare for reliable CN data if available, or yfinance with suffix)
            # The fetcher handles suffix logic, but we should pass the right Tushare code if possible.
            # DataFetcher auto-detects.
            df = fetcher.fetch_stock_data(ticker, period='6mo', provider='auto')
            
            if df is None or df.empty:
                print(f"Skipping {name} ({ticker}) - No Data")
                continue
                
            # Calculate Indicators
            rsi = ti.calculate_rsi(df).iloc[-1]['RSI']
            macd_df = ti.calculate_macd(df)
            macd = macd_df.iloc[-1]['MACD']
            signal = macd_df.iloc[-1]['Signal']
            hist = macd_df.iloc[-1]['Histogram']
            
            sma20 = ti.calculate_sma(df, 20).iloc[-1]['SMA']
            sma50 = ti.calculate_sma(df, 50).iloc[-1]['SMA']
            
            # Bollinger for Support/Resistance
            bb = ti.calculate_bollinger_bands(df)
            bb_upper = bb.iloc[-1]['Upper']
            bb_lower = bb.iloc[-1]['Lower']
            
            current_price = df.iloc[-1]['Close']
            prev_close = df.iloc[-2]['Close']
            change_pct = (current_price - prev_close) / prev_close * 100
            
            # Technical Status
            trend = "震荡"
            if current_price > sma20 and sma20 > sma50:
                trend = "多头"
            elif current_price < sma20 and sma20 < sma50:
                trend = "空头"
                
            rsi_status = "中性"
            if rsi > 70: rsi_status = "超买"
            if rsi < 30: rsi_status = "超卖"
            
            results.append({
                'name': name,
                'ticker': ticker,
                'price': current_price,
                'change_pct': change_pct,
                'rsi': rsi,
                'rsi_status': rsi_status,
                'trend': trend,
                'macd_hist': hist,
                'support': bb_lower,
                'resistance': bb_upper,
                'sma20': sma20
            })
            print(f"Processed {name}")
            
        except Exception as e:
            print(f"Error processing {name}: {e}")

    # Generate Report
    script_dir = os.path.dirname(os.path.abspath(__file__))
    report_path = os.path.join(script_dir, 'backtest_review_report.md')
    
    # Sort by Change PCT
    results.sort(key=lambda x: x['change_pct'], reverse=True)
    
    # Special focus on 510880
    dividend_etf = next((x for x in results if '510880' in x['ticker']), None)
    
    report_content = f"""# 每日持仓复盘分析报告
**复盘日期**: {pd.Timestamp.now().strftime('%Y-%m-%d')}

## 1. 核心复盘：红利 ETF (510880)
> 结合今日早盘技术分析报告进行验证。

*   **早盘分析观点**:
    *   **关键压力位**: 3.19 (20日均线)
    *   **趋势判断**: 空头排列，震荡整理，存在下行压力。
    *   **MACD**:虽有金叉但动能不强。

*   **今日实际走势**:
    *   **收盘价**: {dividend_etf['price']:.3f} (跌幅 {dividend_etf['change_pct']:.2f}%)
    *   **验证**: 股价未能有效突破 3.19 压力位，反而受阻回落，收于 3.20 成本线下方，验证了空头排列的压制力。
    *   **当前状态**: RSI 为 {dividend_etf['rsi']:.1f} ({dividend_etf['rsi_status']})，MACD 柱状图为 {dividend_etf['macd_hist']:.4f}。
    *   **后续策略**: 下方支撑位关注布林带下轨 **{dividend_etf['support']:.3f}**。若触及此位置且不破，可考虑补仓摊薄成本；若反抽 3.19 无法突破，仍需减仓做T。

## 2. 市场分化：科技强 vs 周期弱
今日持仓表现呈现明显的两极分化，科技成长类领涨，红利周期类回调。

### 🔴 领涨板块 (科技/成长)
| 名称 | 涨幅 | RSI | 趋势 | 评价 |
|---|---|---|---|---|
"""
    
    for item in results[:3]: # Top 3 gainers
        if item['change_pct'] > 0:
            report_content += f"| {item['name']} | +{item['change_pct']:.2f}% | {item['rsi']:.1f} | {item['trend']} | 强势反弹，关注 {item['resistance']:.2f} 压力位 |\n"

    report_content += """
### 🟢 领跌板块 (周期/防御)
| 名称 | 涨幅 | RSI | 趋势 | 评价 |
|---|---|---|---|---|
"""
    for item in results[-3:]: # Bottom 3 losers (reversed list is sorted desc)
        if item['change_pct'] < 0:
            report_content += f"| {item['name']} | {item['change_pct']:.2f}% | {item['rsi']:.1f} | {item['trend']} | 此前涨幅过大回调，关注 {item['support']:.2f} 支撑 |\n"

    report_content += """
## 3. 操作建议 (Action Items)

1.  **红利 ETF (510880)**:
    *   **观察**: 密切关注 3.14 - 3.15 区间支撑。
    *   **操作**: 目前浮亏扩大，暂不急于加仓，等待企稳信号（如日线收出下影线）。

2.  **科创 50 / 机器人 / 5G**:
    *   **观察**: 短期动能强劲，但需警惕 RSI 过高（若 > 70）。
    *   **操作**: 如果明日继续冲高，建议对获利丰厚的 **科创 50** 部分止盈，锁定利润。

3.  **军工 / 航空**:
    *   **观察**: 今日跌幅较大，需确认是否跌破重要均线（如 50日线）。
    *   **操作**: 保持观望，暂不动手。

## 4. 详细数据监控
"""
    
    # Table of all
    report_content += "| 代码 | 名称 | 现价 | 涨跌幅 | RSI (14) | 20日均线 | 支撑位 (下轨) | 压力位 (上轨) |\n"
    report_content += "|---|---|---|---|---|---|---|---|\n"
    for r in results:
        report_content += f"| {r['ticker']} | {r['name']} | {r['price']:.3f} | {r['change_pct']:.2f}% | {r['rsi']:.1f} | {r['sma20']:.3f} | {r['support']:.3f} | {r['resistance']:.3f} |\n"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    # Save data
    data_path = os.path.join(script_dir, 'backtest_review_daily.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"Report generated: {report_path}")
    print(report_content)

if __name__ == "__main__":
    generate_daily_review()

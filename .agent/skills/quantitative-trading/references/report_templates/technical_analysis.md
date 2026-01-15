# [标的代码] 技术指标分析
**分析日期**: YYYY-MM-DD (数据截止 YYYY-MM-DD)

## 1. 核心指标状态
*   **当前价格**: [Price]
*   **RSI (14)**: [Value]
    *   *解读*: [如：接近 70 的超买警戒线，显示近期动能强劲，但需警惕回调风险。]
*   **MACD**: [Value] (DIF)
    *   **Signal**: [Value] (DEA)
    *   **Histogram**: [Value]
    *   *解读*: [如：MACD 处于多头区域，且柱状图为正，上升趋势保持中。]

## 2. 趋势与通道
*   **均线系统**:
    *   **SMA 20 (月线)**: [Value]
    *   **SMA 50 (季线)**: [Value]
    *   *状态*: [如：短期均线 > 中期均线，且价格远高于均线，典型的多头排列。]
*   **布林带 (Bollinger Bands)**:
    *   **上轨**: [Value]
    *   *状态*: [如：当前价格位于中轨和上轨之间，且 %B 指标为 0.85，表明处于强势区间。]
*   **CCI**: [Value]
    *   *解读*: [如：大于 100，表明处于非常强势的状态，可能面临短线获利盘抛压。]

## 3. 波动性
*   **ATR (14)**: [Value]
*   **Volatility**: [Value] (年化波动率)

## 4. 📊 生成文件
您可以在以下位置找到详细数据：

*   **完整报告**: `workspace/.../analysis_report.md`
*   **指标数据 (CSV)**: `workspace/.../indicators_[ticker].csv`
*   **分析脚本**: `workspace/.../analyze_[ticker].py`

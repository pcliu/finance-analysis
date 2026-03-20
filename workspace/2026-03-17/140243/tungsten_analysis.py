#!/usr/bin/env python3
"""
钨业四剑客建仓分析 - 技术面综合分析
厦门钨业(600549), 中钨高新(000657), 章源钨业(002378), 洛阳钼业(603993)
"""
import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '../../../.agent/skills/quantitative-trading'))
sys.path.append(SKILL_DIR)

from scripts import (
    fetch_stock_data, fetch_realtime_quote,
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_sma, calculate_atr, calculate_stochastic
)
from scripts import RiskManager
from scripts.utils import make_serializable

# 钨业四剑客
STOCKS = {
    '600549': '厦门钨业',
    '000657': '中钨高新',
    '002378': '章源钨业',
    '603993': '洛阳钼业',
}

def analyze_stock(ticker, name):
    """对单只股票进行全面技术分析"""
    print(f"\n{'='*60}")
    print(f"正在分析: {name} ({ticker})")
    print(f"{'='*60}")
    
    result = {
        'ticker': ticker,
        'name': name,
    }
    
    # 1. 获取实时行情
    try:
        rt = fetch_realtime_quote(ticker)
        if rt is not None and not rt.empty:
            rt_dict = rt.iloc[0].to_dict()
            result['realtime'] = rt_dict
            print(f"实时价格: {rt_dict.get('最新价', 'N/A')}")
            print(f"涨跌幅: {rt_dict.get('涨跌幅', 'N/A')}%")
        else:
            result['realtime'] = None
            print("实时行情获取失败")
    except Exception as e:
        result['realtime'] = None
        print(f"实时行情获取失败: {e}")
    
    # 2. 获取历史数据 (6个月)
    try:
        data = fetch_stock_data(ticker, period='6mo')
        if data is None or data.empty:
            print(f"历史数据获取失败")
            result['error'] = '历史数据获取失败'
            return result
        
        print(f"获取到 {len(data)} 条历史记录")
        
        # 当前价格
        current_price = data['Close'].iloc[-1]
        result['current_price'] = current_price
        
        # 价格变化
        if len(data) >= 5:
            result['price_5d_change'] = (data['Close'].iloc[-1] / data['Close'].iloc[-5] - 1) * 100
        if len(data) >= 20:
            result['price_20d_change'] = (data['Close'].iloc[-1] / data['Close'].iloc[-20] - 1) * 100
        if len(data) >= 60:
            result['price_60d_change'] = (data['Close'].iloc[-1] / data['Close'].iloc[-60] - 1) * 100
        
        # 3. 技术指标
        # RSI
        rsi = calculate_rsi(data, window=14)
        result['rsi_14'] = rsi['RSI'].iloc[-1]
        # RSI 6日 (短期)
        rsi6 = calculate_rsi(data, window=6)
        result['rsi_6'] = rsi6['RSI'].iloc[-1]
        
        print(f"RSI(14): {result['rsi_14']:.2f}")
        print(f"RSI(6): {result['rsi_6']:.2f}")
        
        # MACD
        macd = calculate_macd(data)
        result['macd'] = macd['MACD'].iloc[-1]
        result['macd_signal'] = macd['Signal'].iloc[-1]
        result['macd_histogram'] = macd['Histogram'].iloc[-1]
        
        # MACD 交叉判断
        if len(macd) >= 2:
            prev_hist = macd['Histogram'].iloc[-2]
            curr_hist = macd['Histogram'].iloc[-1]
            if prev_hist < 0 and curr_hist >= 0:
                result['macd_cross'] = '金叉'
            elif prev_hist > 0 and curr_hist < 0:
                result['macd_cross'] = '死叉'
            else:
                result['macd_cross'] = '无交叉'
        
        print(f"MACD: {result['macd']:.4f}, Signal: {result['macd_signal']:.4f}, Histogram: {result['macd_histogram']:.4f}")
        print(f"MACD 信号: {result.get('macd_cross', 'N/A')}")
        
        # Bollinger Bands
        bb = calculate_bollinger_bands(data)
        result['bb_upper'] = bb['Upper'].iloc[-1]
        result['bb_middle'] = bb['Middle'].iloc[-1]
        result['bb_lower'] = bb['Lower'].iloc[-1]
        result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / result['bb_middle'] * 100
        
        # 布林带位置
        bb_position = (current_price - result['bb_lower']) / (result['bb_upper'] - result['bb_lower'])
        result['bb_position'] = bb_position
        
        print(f"布林带: Upper={result['bb_upper']:.2f}, Middle={result['bb_middle']:.2f}, Lower={result['bb_lower']:.2f}")
        print(f"布林带位置: {bb_position:.2%}")
        
        # SMA
        sma5 = calculate_sma(data, window=5)
        sma10 = calculate_sma(data, window=10)
        sma20 = calculate_sma(data, window=20)
        sma60 = calculate_sma(data, window=60)
        result['sma_5'] = sma5['SMA'].iloc[-1]
        result['sma_10'] = sma10['SMA'].iloc[-1]
        result['sma_20'] = sma20['SMA'].iloc[-1]
        result['sma_60'] = sma60['SMA'].iloc[-1]
        
        # 均线多头/空头排列
        if result['sma_5'] > result['sma_10'] > result['sma_20'] > result['sma_60']:
            result['ma_trend'] = '多头排列'
        elif result['sma_5'] < result['sma_10'] < result['sma_20'] < result['sma_60']:
            result['ma_trend'] = '空头排列'
        else:
            result['ma_trend'] = '交织排列'
        
        print(f"均线趋势: {result['ma_trend']}")
        print(f"SMA5={result['sma_5']:.2f}, SMA10={result['sma_10']:.2f}, SMA20={result['sma_20']:.2f}, SMA60={result['sma_60']:.2f}")
        
        # ATR (波动率)
        atr = calculate_atr(data, window=14)
        result['atr_14'] = atr['ATR'].iloc[-1]
        result['atr_pct'] = result['atr_14'] / current_price * 100
        print(f"ATR(14): {result['atr_14']:.2f} ({result['atr_pct']:.2f}%)")
        
        # KDJ / Stochastic
        stoch = calculate_stochastic(data)
        result['stoch_k'] = stoch['K'].iloc[-1]
        result['stoch_d'] = stoch['D'].iloc[-1]
        
        # KDJ 超买超卖
        if result['stoch_k'] > 80:
            result['kdj_signal'] = '超买区'
        elif result['stoch_k'] < 20:
            result['kdj_signal'] = '超卖区'
        else:
            result['kdj_signal'] = '中性'
        
        print(f"KDJ: K={result['stoch_k']:.2f}, D={result['stoch_d']:.2f} ({result['kdj_signal']})")
        
        # 4. 成交量分析
        vol_5 = data['Volume'].iloc[-5:].mean()
        vol_20 = data['Volume'].iloc[-20:].mean()
        result['vol_5d_avg'] = vol_5
        result['vol_20d_avg'] = vol_20
        result['vol_ratio'] = vol_5 / vol_20 if vol_20 > 0 else 0
        
        print(f"成交量比(5日/20日): {result['vol_ratio']:.2f}")
        
        # 5. 风险指标
        rm = RiskManager()
        returns = data['Close'].pct_change().dropna()
        
        # 最大回撤
        dd_metrics = rm.calculate_drawdown_metrics(returns, is_returns=True)
        result['max_drawdown'] = dd_metrics['max_drawdown']
        
        # VaR
        var_95 = rm.calculate_var(returns, confidence_level=0.95)
        result['var_95'] = var_95
        
        # 风险调整指标
        risk_metrics = rm.calculate_risk_adjusted_metrics(returns)
        result['sharpe_ratio'] = risk_metrics.get('sharpe_ratio', None)
        result['sortino_ratio'] = risk_metrics.get('sortino_ratio', None)
        
        print(f"最大回撤: {result['max_drawdown']:.2%}")
        print(f"VaR(95%): {result['var_95']:.4f}")
        print(f"Sharpe Ratio: {result.get('sharpe_ratio', 'N/A')}")
        
        # 6. 近期走势特征
        # 最近是否从高点回调
        max_60d = data['Close'].iloc[-60:].max()
        result['high_60d'] = max_60d
        result['drawdown_from_high'] = (current_price / max_60d - 1) * 100
        
        min_60d = data['Close'].iloc[-60:].min()
        result['low_60d'] = min_60d
        result['rebound_from_low'] = (current_price / min_60d - 1) * 100
        
        print(f"60日最高: {max_60d:.2f}, 距最高回撤: {result['drawdown_from_high']:.2f}%")
        print(f"60日最低: {min_60d:.2f}, 距最低反弹: {result['rebound_from_low']:.2f}%")
        
    except Exception as e:
        result['error'] = str(e)
        print(f"分析失败: {e}")
        import traceback
        traceback.print_exc()
    
    return result


def main():
    print("=" * 60)
    print("钨业四剑客建仓分析")
    print(f"分析时间: 2026-03-17")
    print("=" * 60)
    
    results = {}
    
    for ticker, name in STOCKS.items():
        result = analyze_stock(ticker, name)
        results[ticker] = result
    
    # 保存结果
    clean_results = make_serializable(results)
    output_path = os.path.join(SCRIPT_DIR, 'tungsten_analysis_data.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(clean_results, f, indent=4, ensure_ascii=False)
    
    print(f"\n\n结果已保存到: {output_path}")
    
    # 打印综合建议
    print("\n" + "=" * 60)
    print("综合技术信号汇总")
    print("=" * 60)
    
    for ticker, r in results.items():
        name = r.get('name', ticker)
        print(f"\n--- {name} ({ticker}) ---")
        
        if 'error' in r:
            print(f"  ⚠️ 分析失败: {r['error']}")
            continue
        
        # 汇总评分
        signals = []
        
        # RSI 信号
        rsi = r.get('rsi_14', 50)
        if rsi < 30:
            signals.append(('RSI', '超卖(买入信号)', 2))
        elif rsi < 40:
            signals.append(('RSI', '偏低(关注)', 1))
        elif rsi > 70:
            signals.append(('RSI', '超买(卖出信号)', -2))
        elif rsi > 60:
            signals.append(('RSI', '偏高(谨慎)', -1))
        else:
            signals.append(('RSI', '中性', 0))
        
        # MACD 信号
        macd_cross = r.get('macd_cross', '无交叉')
        if macd_cross == '金叉':
            signals.append(('MACD', '金叉(买入)', 2))
        elif macd_cross == '死叉':
            signals.append(('MACD', '死叉(卖出)', -2))
        elif r.get('macd_histogram', 0) > 0:
            signals.append(('MACD', '柱状图为正', 1))
        else:
            signals.append(('MACD', '柱状图为负', -1))
        
        # 布林带信号
        bb_pos = r.get('bb_position', 0.5)
        if bb_pos < 0.1:
            signals.append(('布林带', '接近下轨(超卖)', 2))
        elif bb_pos < 0.3:
            signals.append(('布林带', '下半区', 1))
        elif bb_pos > 0.9:
            signals.append(('布林带', '接近上轨(超买)', -2))
        elif bb_pos > 0.7:
            signals.append(('布林带', '上半区', -1))
        else:
            signals.append(('布林带', '中轨附近', 0))
        
        # 均线信号
        ma_trend = r.get('ma_trend', '交织排列')
        if ma_trend == '多头排列':
            signals.append(('均线', '多头排列(上升趋势)', 1))
        elif ma_trend == '空头排列':
            signals.append(('均线', '空头排列(下降趋势)', -1))
        else:
            signals.append(('均线', '交织(震荡)', 0))
        
        # KDJ 信号
        kdj = r.get('kdj_signal', '中性')
        if kdj == '超卖区':
            signals.append(('KDJ', '超卖(买入信号)', 2))
        elif kdj == '超买区':
            signals.append(('KDJ', '超买(卖出信号)', -2))
        else:
            signals.append(('KDJ', '中性', 0))
        
        # 成交量信号
        vol_ratio = r.get('vol_ratio', 1)
        if vol_ratio > 1.5:
            signals.append(('成交量', f'放量({vol_ratio:.1f}x)', 0))  # neutral - depends on context
        elif vol_ratio < 0.5:
            signals.append(('成交量', f'缩量({vol_ratio:.1f}x)', 0))
        else:
            signals.append(('成交量', f'正常({vol_ratio:.1f}x)', 0))
        
        # 回撤信号
        dd = r.get('drawdown_from_high', 0)
        if dd < -30:
            signals.append(('回撤', f'深度回调({dd:.1f}%)', 2))
        elif dd < -15:
            signals.append(('回撤', f'显著回调({dd:.1f}%)', 1))
        elif dd > -5:
            signals.append(('回撤', f'接近高点({dd:.1f}%)', -1))
        else:
            signals.append(('回撤', f'温和回调({dd:.1f}%)', 0))
        
        # 打印信号
        total_score = 0
        for sig_name, sig_desc, sig_score in signals:
            emoji = '🟢' if sig_score > 0 else ('🔴' if sig_score < 0 else '⚪')
            print(f"  {emoji} {sig_name}: {sig_desc} (得分:{sig_score:+d})")
            total_score += sig_score
        
        print(f"  📊 综合得分: {total_score:+d}")
        
        if total_score >= 4:
            print(f"  🟢 建议: 强烈买入信号")
        elif total_score >= 2:
            print(f"  🟢 建议: 偏多，可以考虑建仓")
        elif total_score >= 0:
            print(f"  ⚪ 建议: 中性，观望为主")
        elif total_score >= -2:
            print(f"  🟡 建议: 偏空，谨慎观望")
        else:
            print(f"  🔴 建议: 避免建仓")


if __name__ == '__main__':
    main()

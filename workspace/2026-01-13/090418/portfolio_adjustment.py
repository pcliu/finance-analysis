#!/usr/bin/env python3
"""
投资组合分析脚本 - 2026-01-13
功能：
1. 获取现有持仓和候选品种的技术指标
2. 复盘历史策略建议与实际行情拟合度
3. 动态调整风控阈值
4. 生成操作建议（限1万元预算）
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 设置路径
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading')

from scripts import (
    fetch_stock_data, 
    calculate_rsi, 
    calculate_sma, 
    calculate_ema,
    calculate_macd, 
    calculate_bollinger_bands
)

# 输出目录
OUTPUT_DIR = '/Users/liupengcheng/Documents/Code/finance-analysis/.agent/skills/quantitative-trading/workspace/2026-01-13/090418'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============ 持仓数据 (来自用户截图) ============
CURRENT_HOLDINGS = {
    '510150.SS': {'name': '消费ETF', 'shares': 5000, 'market_value': 2885.00, 'pnl_pct': 0.33},
    '510880.SS': {'name': '红利ETF', 'shares': 1000, 'market_value': 3231.00, 'pnl_pct': 0.80},
    '513180.SS': {'name': '恒指科技', 'shares': 800, 'market_value': 617.60, 'pnl_pct': 0.44},
    '513630.SS': {'name': '香港红利', 'shares': 500, 'market_value': 807.00, 'pnl_pct': -0.25},
    '515050.SS': {'name': '5GETF', 'shares': 1000, 'market_value': 2381.00, 'pnl_pct': 2.63},
    '515070.SS': {'name': 'AI智能', 'shares': 500, 'market_value': 1079.50, 'pnl_pct': 8.44},
    '588000.SS': {'name': '科创50', 'shares': 4000, 'market_value': 6376.00, 'pnl_pct': 25.96},
    '159770.SZ': {'name': '机器人AI', 'shares': 1000, 'market_value': 1133.00, 'pnl_pct': 6.04},
    '159830.SZ': {'name': '上海金', 'shares': 400, 'market_value': 4076.00, 'pnl_pct': 4.81},
    '161226.SZ': {'name': '白银基金', 'shares': 300, 'market_value': 813.00, 'pnl_pct': 25.87},
}

# ============ 非持仓候选 (来自 ETFs.csv) ============
NON_HOLDING_CANDIDATES = {
    '512660.SS': {'name': '军工ETF'},
    '159241.SZ': {'name': '航空航天ETF'},
    '159352.SZ': {'name': 'A500ETF南方'},
    '159326.SZ': {'name': '电网设备ETF'},
    '159516.SZ': {'name': '半导体设备ETF'},
    '512400.SS': {'name': '有色金属ETF'},
    '518880.SS': {'name': '黄金ETF'},
}

# ============ 历史建议记录 (用于复盘) ============
HISTORICAL_RECOMMENDATIONS = {
    '2026-01-07': {
        '159241.SZ': {'action': 'AVOID', 'rsi': 82.31, 'reason': '严重超买'},
        '159516.SZ': {'action': 'REDUCE', 'rsi': 74.27, 'shares': 300},
        '161226.SZ': {'action': 'REDUCE', 'rsi': 62.41, 'shares': 200},
    },
    '2026-01-09': {
        '159516.SZ': {'action': 'SELL_ALL', 'rsi': 78.64, 'reason': '严重超买清仓'},
        '159241.SZ': {'action': 'AVOID', 'rsi': 83.97, 'reason': '继续超买'},
        '588000.SS': {'action': 'REDUCE', 'rsi': 70.43, 'shares': 2000},
    },
    '2026-01-12': {
        '159241.SZ': {'action': 'AVOID', 'rsi': 86.87, 'reason': '严重超买勿追高'},
        '512660.SS': {'action': 'AVOID', 'rsi': 86.51, 'reason': '严重超买'},
        '510150.SS': {'action': 'BUY', 'rsi': 63.33, 'shares': 5000},
        '512400.SS': {'action': 'SELL_ALL', 'shares': 700, 'reason': 'RSI超买止盈'},
        '588000.SS': {'action': 'REDUCE', 'shares': 2000, 'reason': '减持锁定利润'},
    }
}

def get_technical_indicators(ticker, period='3mo'):
    """获取单个品种的技术指标"""
    try:
        data = fetch_stock_data(ticker, period=period)
        if data is None or len(data) < 20:
            return None
        
        rsi = calculate_rsi(data, period=14)  # Fixed: use period instead of window
        sma_20 = calculate_sma(data, window=20)
        sma_5 = calculate_sma(data, window=5)
        ema_12 = calculate_ema(data, window=12)  # Fixed: use window instead of span
        macd = calculate_macd(data)
        bb = calculate_bollinger_bands(data, window=20, num_std=2)
        
        current_price = float(data['Close'].iloc[-1])
        
        # 计算涨跌幅
        price_5d_ago = float(data['Close'].iloc[-6]) if len(data) >= 6 else current_price
        price_20d_ago = float(data['Close'].iloc[-21]) if len(data) >= 21 else current_price
        
        change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
        change_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
        
        # 趋势判断
        macd_line = float(macd['MACD'].iloc[-1])
        signal_line = float(macd['Signal'].iloc[-1])
        bb_upper = float(bb['Upper'].iloc[-1])
        bb_lower = float(bb['Lower'].iloc[-1])
        bb_middle = float(bb['Middle'].iloc[-1])
        
        if macd_line > signal_line and current_price > sma_20.iloc[-1]:
            trend = '强势上涨'
        elif macd_line > signal_line:
            trend = '上涨'
        elif macd_line < signal_line and current_price < sma_20.iloc[-1]:
            trend = '下跌'
        else:
            trend = '震荡'
        
        # 动量判断
        if macd_line > 0 and macd_line > signal_line:
            momentum = '强'
        elif macd_line > 0:
            momentum = '中'
        else:
            momentum = '弱'
        
        return {
            'price': current_price,
            'rsi': float(rsi.iloc[-1]),
            'sma_5': float(sma_5.iloc[-1]),
            'sma_20': float(sma_20.iloc[-1]),
            'macd': macd_line,
            'macd_signal': signal_line,
            'macd_histogram': float(macd['Histogram'].iloc[-1]),
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower,
            'bb_position': (current_price - bb_lower) / (bb_upper - bb_lower) * 100 if bb_upper != bb_lower else 50,
            'change_5d': change_5d,
            'change_20d': change_20d,
            'trend': trend,
            'momentum': momentum,
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def calculate_backtest_accuracy():
    """计算历史建议的拟合度"""
    results = {}
    
    # 计算各品种从建议日期到今天的实际走势
    backtest_items = [
        # 1月7日建议
        ('159241.SZ', '2026-01-07', 'AVOID', '建议观望超买品种'),
        ('159516.SZ', '2026-01-07', 'REDUCE', '建议减持超买品种'),
        # 1月9日建议  
        ('159516.SZ', '2026-01-09', 'SELL_ALL', '建议清仓超买品种'),
        ('588000.SS', '2026-01-09', 'REDUCE', '建议减持科创50'),
        # 1月12日建议
        ('510150.SS', '2026-01-12', 'BUY', '建议买入消费ETF'),
        ('512400.SS', '2026-01-12', 'SELL_ALL', '建议清仓有色ETF'),
    ]
    
    for ticker, rec_date, action, description in backtest_items:
        try:
            data = fetch_stock_data(ticker, period='1mo')
            if data is None or len(data) < 2:
                continue
            
            current_price = float(data['Close'].iloc[-1])
            # 找到建议日期附近的价格
            rec_dt = datetime.strptime(rec_date, '%Y-%m-%d')
            
            # 获取历史价格
            for i, idx in enumerate(data.index):
                idx_date = idx.date() if hasattr(idx, 'date') else idx
                try:
                    if str(idx_date) >= rec_date:
                        rec_price = float(data['Close'].iloc[i])
                        break
                except:
                    continue
            else:
                rec_price = float(data['Close'].iloc[0])
            
            price_change_pct = ((current_price - rec_price) / rec_price) * 100
            
            # 评估建议效果
            if action in ['AVOID', 'SELL_ALL', 'REDUCE']:
                # 如果建议卖出/观望，而价格下跌，则建议正确
                is_correct = price_change_pct < 0
                effectiveness = 'CORRECT' if is_correct else 'MISSED_GAIN' if price_change_pct > 5 else 'NEUTRAL'
            else:  # BUY
                is_correct = price_change_pct > 0
                effectiveness = 'CORRECT' if is_correct else 'LOSS' if price_change_pct < -3 else 'NEUTRAL'
            
            results[f"{ticker}_{rec_date}"] = {
                'ticker': ticker,
                'rec_date': rec_date,
                'action': action,
                'description': description,
                'rec_price': rec_price,
                'current_price': current_price,
                'price_change_pct': price_change_pct,
                'effectiveness': effectiveness,
            }
        except Exception as e:
            print(f"Backtest error for {ticker}: {e}")
    
    return results

def adjust_risk_thresholds(backtest_results):
    """根据复盘结果动态调整风控阈值"""
    
    # 基础阈值
    base_thresholds = {
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'rsi_severe_overbought': 80,
        'stop_loss_pct': -8,
        'take_profit_pct': 25,
        'max_single_position_pct': 30,
        'max_sector_exposure_pct': 40,
    }
    
    # 分析复盘结果
    correct_count = sum(1 for r in backtest_results.values() if r['effectiveness'] == 'CORRECT')
    total_count = len(backtest_results)
    accuracy = correct_count / total_count if total_count > 0 else 0.5
    
    # 如果准确率高，可以适当放松阈值；准确率低则收紧
    adjustment = 1.0
    if accuracy >= 0.7:
        adjustment = 1.05  # 放松5%
    elif accuracy < 0.5:
        adjustment = 0.95  # 收紧5%
    
    adjusted_thresholds = {
        'rsi_overbought': int(base_thresholds['rsi_overbought'] * adjustment),
        'rsi_oversold': int(base_thresholds['rsi_oversold'] / adjustment),
        'rsi_severe_overbought': int(base_thresholds['rsi_severe_overbought'] * adjustment),
        'stop_loss_pct': base_thresholds['stop_loss_pct'] * adjustment,
        'take_profit_pct': base_thresholds['take_profit_pct'],
        'max_single_position_pct': base_thresholds['max_single_position_pct'],
        'max_sector_exposure_pct': base_thresholds['max_sector_exposure_pct'],
        'backtest_accuracy': accuracy,
        'adjustment_factor': adjustment,
    }
    
    return adjusted_thresholds

def generate_recommendations(holdings_analysis, candidates_analysis, thresholds, budget=10000):
    """生成操作建议"""
    
    sell_recommendations = []
    buy_recommendations = []
    hold_recommendations = []
    
    total_sell_amount = 0
    total_buy_amount = 0
    
    rsi_overbought = thresholds['rsi_overbought']
    rsi_severe = thresholds['rsi_severe_overbought']
    
    # 分析持仓
    for ticker, info in holdings_analysis.items():
        if info is None:
            continue
        
        holding = CURRENT_HOLDINGS.get(ticker, {})
        name = holding.get('name', ticker)
        shares = holding.get('shares', 0)
        market_value = holding.get('market_value', 0)
        pnl_pct = holding.get('pnl_pct', 0)
        
        rsi = info['rsi']
        trend = info['trend']
        price = info['price']
        
        # 判断操作建议
        if rsi >= rsi_severe:
            # 严重超买 - 建议减持
            reduce_pct = 0.5 if pnl_pct > 20 else 0.3
            reduce_shares = int(shares * reduce_pct / 100) * 100  # 取整到100股
            if reduce_shares >= 100:
                sell_amount = reduce_shares * price
                sell_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '减持',
                    'shares': reduce_shares,
                    'price_range': f"{price*0.98:.3f} - {price*1.02:.3f}",
                    'amount': sell_amount,
                    'reason': f"RSI={rsi:.1f} 严重超买，盈利{pnl_pct:.1f}%锁定部分利润",
                    'rsi': rsi,
                    'trend': trend,
                })
                total_sell_amount += sell_amount
        elif rsi >= rsi_overbought:
            # 超买 - 观察但可减持
            if pnl_pct > 15:
                reduce_shares = int(shares * 0.2 / 100) * 100
                if reduce_shares >= 100:
                    sell_amount = reduce_shares * price
                    sell_recommendations.append({
                        'ticker': ticker,
                        'name': name,
                        'action': '适度减持',
                        'shares': reduce_shares,
                        'price_range': f"{price*0.98:.3f} - {price*1.02:.3f}",
                        'amount': sell_amount,
                        'reason': f"RSI={rsi:.1f} 超买区，锁定部分利润",
                        'rsi': rsi,
                        'trend': trend,
                    })
                    total_sell_amount += sell_amount
            else:
                hold_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '观察持有',
                    'reason': f"RSI={rsi:.1f} 偏高但趋势{trend}",
                    'rsi': rsi,
                    'trend': trend,
                })
        elif trend == '下跌' and rsi < 45:
            # 弱势品种 - 考虑换仓
            hold_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '观望',
                'reason': f"趋势{trend}，RSI={rsi:.1f}，可考虑换强",
                'rsi': rsi,
                'trend': trend,
            })
        else:
            # 健康区间 - 继续持有
            hold_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '持有',
                'reason': f"RSI={rsi:.1f} 健康区间，趋势{trend}",
                'rsi': rsi,
                'trend': trend,
            })
    
    # 分析候选品种
    available_budget = budget + total_sell_amount
    
    # 按 RSI 升序排列（优先低估值）
    sorted_candidates = sorted(
        [(t, i) for t, i in candidates_analysis.items() if i is not None],
        key=lambda x: x[1]['rsi']
    )
    
    for ticker, info in sorted_candidates:
        if total_buy_amount >= available_budget:
            break
        
        name = NON_HOLDING_CANDIDATES.get(ticker, {}).get('name', ticker)
        rsi = info['rsi']
        trend = info['trend']
        price = info['price']
        change_5d = info['change_5d']
        change_20d = info['change_20d']
        
        # 评估建仓可行性
        if rsi >= rsi_severe:
            # 严重超买 - 不建仓
            buy_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '不建仓',
                'feasibility': '❌ 不推荐',
                'reason': f"RSI={rsi:.1f} 严重超买，追高风险极大",
                'wait_condition': f"等待回调至RSI<{rsi_overbought-5}",
                'rsi': rsi,
                'trend': trend,
                'price': price,
            })
        elif rsi >= rsi_overbought:
            # 超买 - 等待回调
            buy_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '等待回调',
                'feasibility': '⚠️ 观望',
                'reason': f"RSI={rsi:.1f} 超买区，{trend}但需回调",
                'wait_condition': f"等待价格回调至{price*0.92:.3f}附近",
                'rsi': rsi,
                'trend': trend,
                'price': price,
            })
        elif rsi >= 50 and trend in ['上涨', '强势上涨']:
            # 中性偏强 - 可小仓位建仓
            max_buy_amount = min(3000, available_budget - total_buy_amount)
            shares = int(max_buy_amount / price / 100) * 100
            if shares >= 100:
                buy_amount = shares * price
                buy_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '可建仓',
                    'feasibility': '✅ 推荐',
                    'shares': shares,
                    'price_range': f"{price*0.98:.3f} - {price:.3f}",
                    'amount': buy_amount,
                    'reason': f"RSI={rsi:.1f} 健康区间，{trend}",
                    'rsi': rsi,
                    'trend': trend,
                    'price': price,
                })
                total_buy_amount += buy_amount
        elif rsi < 40:
            # 超卖区 - 可布局
            max_buy_amount = min(4000, available_budget - total_buy_amount)
            shares = int(max_buy_amount / price / 100) * 100
            if shares >= 100:
                buy_amount = shares * price
                buy_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '可左侧建仓',
                    'feasibility': '✅ 布局',
                    'shares': shares,
                    'price_range': f"{price*0.97:.3f} - {price:.3f}",
                    'amount': buy_amount,
                    'reason': f"RSI={rsi:.1f} 偏低，逢低布局",
                    'rsi': rsi,
                    'trend': trend,
                    'price': price,
                })
                total_buy_amount += buy_amount
        else:
            buy_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '观望',
                'feasibility': '⚪ 中性',
                'reason': f"RSI={rsi:.1f}，{trend}，无明显建仓时机",
                'rsi': rsi,
                'trend': trend,
                'price': price,
            })
    
    return {
        'sell': sell_recommendations,
        'buy': buy_recommendations,
        'hold': hold_recommendations,
        'total_sell_amount': total_sell_amount,
        'total_buy_amount': total_buy_amount,
        'net_investment': total_buy_amount - total_sell_amount,
    }


def main():
    print("=" * 60)
    print("投资组合分析 - 2026-01-13")
    print("=" * 60)
    
    # 1. 获取持仓品种技术指标
    print("\n[1/5] 获取持仓品种技术指标...")
    holdings_analysis = {}
    for ticker, info in CURRENT_HOLDINGS.items():
        print(f"  正在分析 {info['name']} ({ticker})...")
        holdings_analysis[ticker] = get_technical_indicators(ticker)
    
    # 2. 获取候选品种技术指标
    print("\n[2/5] 获取候选品种技术指标...")
    candidates_analysis = {}
    for ticker, info in NON_HOLDING_CANDIDATES.items():
        print(f"  正在分析 {info['name']} ({ticker})...")
        candidates_analysis[ticker] = get_technical_indicators(ticker)
    
    # 3. 复盘历史建议
    print("\n[3/5] 复盘历史建议拟合度...")
    backtest_results = calculate_backtest_accuracy()
    
    # 4. 调整风控阈值
    print("\n[4/5] 动态调整风控阈值...")
    risk_thresholds = adjust_risk_thresholds(backtest_results)
    print(f"  复盘准确率: {risk_thresholds['backtest_accuracy']*100:.1f}%")
    print(f"  RSI超买阈值: {risk_thresholds['rsi_overbought']}")
    print(f"  RSI严重超买阈值: {risk_thresholds['rsi_severe_overbought']}")
    
    # 5. 生成操作建议
    print("\n[5/5] 生成操作建议...")
    recommendations = generate_recommendations(
        holdings_analysis, 
        candidates_analysis, 
        risk_thresholds,
        budget=10000
    )
    
    # 汇总结果
    result = {
        'analysis_time': datetime.now().isoformat(),
        'holdings_analysis': {k: v for k, v in holdings_analysis.items() if v is not None},
        'candidates_analysis': {k: v for k, v in candidates_analysis.items() if v is not None},
        'backtest_results': backtest_results,
        'risk_thresholds': risk_thresholds,
        'recommendations': recommendations,
        'budget_limit': 10000,
    }
    
    # 保存结果
    output_file = os.path.join(OUTPUT_DIR, 'analysis_result.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✅ 分析完成！结果保存至: {output_file}")
    
    # 打印摘要
    print("\n" + "=" * 60)
    print("分析摘要")
    print("=" * 60)
    
    print(f"\n总持仓市值: {sum(h['market_value'] for h in CURRENT_HOLDINGS.values()):.2f} 元")
    print(f"预算限制: ≤ {result['budget_limit']} 元")
    print(f"复盘准确率: {risk_thresholds['backtest_accuracy']*100:.1f}%")
    
    print(f"\n减仓建议: {len(recommendations['sell'])} 项，预计回笼 {recommendations['total_sell_amount']:.0f} 元")
    print(f"建仓建议: {len([b for b in recommendations['buy'] if b.get('shares')])} 项，预计支出 {recommendations['total_buy_amount']:.0f} 元")
    print(f"净增投资: {recommendations['net_investment']:.0f} 元")
    
    return result


if __name__ == '__main__':
    result = main()

#!/usr/bin/env python3
"""
投资组合分析脚本 - 2026-01-14
功能：
1. 获取现有持仓和候选品种的技术指标
2. 复盘历史策略建议与实际行情拟合度(1/5,1/7,1/9,1/12,1/13)
3. 动态调整风控阈值（基于复盘结果调整：RSI超买68，严重超买78）
4. 生成操作建议（限1万元增量资金）
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 设置路径
sys.path.insert(0, '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading')

from scripts import (
    fetch_stock_data, 
    calculate_rsi, 
    calculate_sma, 
    calculate_ema,
    calculate_macd, 
    calculate_bollinger_bands
)

# 输出目录
OUTPUT_DIR = '/Users/liupengcheng/Documents/Code/finance-analysis/quantitative-trading-skills/quantitative-trading/workspace/2026-01-14/093446'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============ 持仓数据 (来自用户截图 2026-01-14 08:40) ============
CURRENT_HOLDINGS = {
    '510150.SS': {'name': '消费ETF', 'shares': 5000, 'market_value': 2875.00, 'pnl_pct': -0.02},
    '510880.SS': {'name': '红利ETF', 'shares': 1000, 'market_value': 3229.00, 'pnl_pct': 0.73},
    '513180.SS': {'name': '恒指科技', 'shares': 800, 'market_value': 617.60, 'pnl_pct': 0.44},
    '513630.SS': {'name': '香港红利', 'shares': 500, 'market_value': 812.00, 'pnl_pct': 0.37},
    '515050.SS': {'name': '5GETF', 'shares': 1000, 'market_value': 2301.00, 'pnl_pct': -0.82},
    '515070.SS': {'name': 'AI智能', 'shares': 400, 'market_value': 838.40, 'pnl_pct': 8.11},
    '588000.SS': {'name': '科创50', 'shares': 2000, 'market_value': 3098.00, 'pnl_pct': 63.02},
    '159770.SZ': {'name': '机器人AI', 'shares': 700, 'market_value': 781.20, 'pnl_pct': 7.24},
    '159830.SZ': {'name': '上海金', 'shares': 400, 'market_value': 4084.00, 'pnl_pct': 5.02},
    '161226.SZ': {'name': '白银基金', 'shares': 300, 'market_value': 824.40, 'pnl_pct': 27.64},
}

ACCOUNT_INFO = {
    'total_assets': 94376.52,
    'market_value': 19460.60,
    'available_cash': 74915.92,
    'total_pnl': 1737.39,
}

# ============ 非持仓候选 (来自 ETFs.csv，排除已持仓) ============
NON_HOLDING_CANDIDATES = {
    '512660.SS': {'name': '军工ETF'},
    '159241.SZ': {'name': '航空航天ETF天弘'},
    '159352.SZ': {'name': 'A500ETF南方'},
    '159326.SZ': {'name': '电网设备ETF'},
    '159516.SZ': {'name': '半导体设备ETF'},
    '512400.SS': {'name': '有色金属ETF'},
    '518880.SS': {'name': '黄金ETF'},
}

# ============ 历史建议记录 (用于复盘: 1/5, 1/7, 1/9, 1/12, 1/13) ============
HISTORICAL_RECOMMENDATIONS = {
    '2026-01-05': {
        '513180.SS': {'action': 'SELL_ALL', 'reason': '趋势向下减仓'},
        '513630.SS': {'action': 'SELL_ALL', 'reason': '表现不及A股红利'},
        '161226.SZ': {'action': 'BUY', 'price': 2.00, 'shares': 2000, 'reason': '高弹性进攻'},
        '515070.SS': {'action': 'BUY', 'price': 1.95, 'shares': 5000, 'reason': 'AI长期逻辑'},
        '515050.SS': {'action': 'BUY', 'price': 2.28, 'shares': 3000, 'reason': '通信主线'},
        '159770.SZ': {'action': 'BUY', 'price': 1.06, 'shares': 5000, 'reason': '新兴成长'},
    },
    '2026-01-07': {
        '159241.SZ': {'action': 'AVOID', 'rsi': 82.31, 'reason': '严重超买RSI>80'},
        '159516.SZ': {'action': 'REDUCE', 'rsi': 74.27, 'shares': 300, 'reason': '接近超买冲高减仓'},
        '161226.SZ': {'action': 'REDUCE', 'rsi': 62.41, 'shares': 200, 'reason': '高波动降低仓位'},
    },
    '2026-01-09': {
        '159516.SZ': {'action': 'SELL_ALL', 'rsi': 78.64, 'reason': '严重超买清仓'},
        '159241.SZ': {'action': 'AVOID', 'rsi': 83.97, 'reason': '持续超买不建仓'},
        '588000.SS': {'action': 'REDUCE', 'rsi': 70.43, 'shares': 2000, 'reason': '主力仓位需警惕'},
    },
    '2026-01-12': {
        '159241.SZ': {'action': 'AVOID', 'rsi': 86.87, 'reason': '严重超买勿追高'},
        '512660.SS': {'action': 'AVOID', 'rsi': 86.51, 'reason': '严重超买'},
        '510150.SS': {'action': 'BUY', 'price': 0.575, 'shares': 5000, 'reason': 'RSI健康建仓'},
        '512400.SS': {'action': 'SELL_ALL', 'reason': 'RSI超买止盈'},
        '588000.SS': {'action': 'REDUCE', 'shares': 2000, 'reason': '减持锁定利润'},
    },
    '2026-01-13': {
        '515070.SS': {'action': 'REDUCE', 'rsi': 78.6, 'shares': 100, 'reason': '严重超买减持'},
        '588000.SS': {'action': 'REDUCE', 'rsi': 77.2, 'shares': 2000, 'reason': '严重超买减持'},
        '159770.SZ': {'action': 'REDUCE', 'rsi': 76.6, 'shares': 300, 'reason': '严重超买减持'},
    }
}

# ============ 动态调整后的风控阈值（基于复盘结果） ============
# 复盘发现：
# - 超买警告有效（1/13建议减持后确实回调）
# - 航空航天持续错过涨幅（可能过于保守）
# - 建仓时机准确（白银/AI/机器人涨幅可观）
ADJUSTED_RISK_THRESHOLDS = {
    'rsi_overbought': 68,           # 从66调整至68（略宽松）
    'rsi_severe_overbought': 78,    # 从76调整至78（略宽松）
    'rsi_oversold': 30,
    'stop_loss_pct': -8.0,          # 恢复标准阈值
    'new_position_rsi_max': 63,     # 新建仓RSI上限（保守建仓）
    'take_profit_pct': 25,
    'max_single_position_pct': 30,
}


def get_technical_indicators(ticker, period='3mo'):
    """获取单个品种的技术指标"""
    try:
        data = fetch_stock_data(ticker, period=period)
        if data is None or len(data) < 20:
            return None
        
        rsi = calculate_rsi(data, period=14)
        sma_20 = calculate_sma(data, window=20)
        sma_5 = calculate_sma(data, window=5)
        ema_12 = calculate_ema(data, window=12)
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
    """计算1/5, 1/7, 1/9, 1/12, 1/13历史建议的拟合度"""
    results = []
    
    # 定义复盘项目
    backtest_items = [
        # 1月5日建议
        ('513180.SS', '2026-01-05', 'SELL_ALL', '建议清仓恒指科技', 0.75),
        ('513630.SS', '2026-01-05', 'SELL_ALL', '建议清仓香港红利', 1.62),
        ('161226.SZ', '2026-01-05', 'BUY', '建议买入白银', 2.00),
        ('515070.SS', '2026-01-05', 'BUY', '建议买入AI智能', 1.95),
        ('159770.SZ', '2026-01-05', 'BUY', '建议买入机器人', 1.06),
        # 1月7日建议
        ('159241.SZ', '2026-01-07', 'AVOID', '建议观望航空航天', 1.46),
        ('159516.SZ', '2026-01-07', 'REDUCE', '建议减持半导体设备', 1.68),
        ('161226.SZ', '2026-01-07', 'REDUCE', '建议减持白银', 2.55),
        # 1月9日建议
        ('159516.SZ', '2026-01-09', 'SELL_ALL', '建议清仓半导体设备', 1.80),
        ('588000.SS', '2026-01-09', 'REDUCE', '建议减持科创50', 1.55),
        ('159241.SZ', '2026-01-09', 'AVOID', '建议继续观望航空航天', 1.53),
        # 1月12日建议
        ('510150.SS', '2026-01-12', 'BUY', '建议买入消费ETF', 0.575),
        ('512400.SS', '2026-01-12', 'SELL_ALL', '建议清仓有色ETF', 2.10),
        ('588000.SS', '2026-01-12', 'REDUCE', '建议减持科创50', 1.55),
        # 1月13日建议
        ('515070.SS', '2026-01-13', 'REDUCE', '建议减持AI智能', 2.16),
        ('588000.SS', '2026-01-13', 'REDUCE', '建议减持科创50', 1.59),
        ('159770.SZ', '2026-01-13', 'REDUCE', '建议减持机器人', 1.13),
    ]
    
    for ticker, rec_date, action, description, rec_price in backtest_items:
        try:
            data = fetch_stock_data(ticker, period='1mo')
            if data is None or len(data) < 2:
                continue
            
            current_price = float(data['Close'].iloc[-1])
            price_change_pct = ((current_price - rec_price) / rec_price) * 100
            
            # 评估建议效果
            if action in ['AVOID', 'SELL_ALL', 'REDUCE']:
                if price_change_pct < -2:
                    effectiveness = 'CORRECT'
                    emoji = '✅'
                elif price_change_pct > 5:
                    effectiveness = 'MISSED_GAIN'
                    emoji = '⚠️'
                else:
                    effectiveness = 'NEUTRAL'
                    emoji = '⚪'
            else:  # BUY
                if price_change_pct > 3:
                    effectiveness = 'CORRECT'
                    emoji = '✅'
                elif price_change_pct < -5:
                    effectiveness = 'LOSS'
                    emoji = '❌'
                else:
                    effectiveness = 'NEUTRAL'
                    emoji = '⚪'
            
            results.append({
                'ticker': ticker,
                'rec_date': rec_date,
                'action': action,
                'description': description,
                'rec_price': rec_price,
                'current_price': current_price,
                'price_change_pct': round(price_change_pct, 2),
                'effectiveness': effectiveness,
                'emoji': emoji,
            })
        except Exception as e:
            print(f"Backtest error for {ticker}: {e}")
    
    return results


def generate_recommendations(holdings_analysis, candidates_analysis, thresholds, budget=10000):
    """生成操作建议"""
    
    sell_recommendations = []
    buy_recommendations = []
    hold_recommendations = []
    
    total_sell_amount = 0
    total_buy_amount = 0
    
    rsi_overbought = thresholds['rsi_overbought']
    rsi_severe = thresholds['rsi_severe_overbought']
    new_position_rsi_max = thresholds['new_position_rsi_max']
    
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
        change_5d = info['change_5d']
        
        # 判断操作建议
        if rsi >= rsi_severe:
            # 严重超买 - 建议减持
            reduce_pct = 0.4 if pnl_pct > 20 else 0.25
            reduce_shares = int(shares * reduce_pct / 100) * 100
            if reduce_shares >= 100:
                sell_amount = reduce_shares * price
                sell_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '减持',
                    'shares': reduce_shares,
                    'price_range': f"{price*0.98:.3f} - {price*1.02:.3f}",
                    'amount': round(sell_amount, 2),
                    'reason': f"RSI={rsi:.1f} 严重超买(>{rsi_severe})，盈利{pnl_pct:.1f}%锁定利润",
                    'rsi': round(rsi, 1),
                    'trend': trend,
                    'change_5d': round(change_5d, 2),
                })
                total_sell_amount += sell_amount
        elif rsi >= rsi_overbought:
            # 超买区间 - 观察
            hold_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '观察持有',
                'reason': f"RSI={rsi:.1f} 超买区({rsi_overbought}-{rsi_severe})，趋势{trend}，注意回调风险",
                'rsi': round(rsi, 1),
                'trend': trend,
                'change_5d': round(change_5d, 2),
            })
        elif trend == '下跌' and rsi < 45:
            # 弱势品种
            hold_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '观望',
                'reason': f"趋势{trend}，RSI={rsi:.1f}偏弱，可考虑换强",
                'rsi': round(rsi, 1),
                'trend': trend,
                'change_5d': round(change_5d, 2),
            })
        else:
            # 健康区间 - 继续持有
            hold_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '持有',
                'reason': f"RSI={rsi:.1f} 健康区间，趋势{trend}",
                'rsi': round(rsi, 1),
                'trend': trend,
                'change_5d': round(change_5d, 2),
            })
    
    # 分析候选品种建仓可行性
    available_budget = budget  # 不使用减持资金，严格控制增量
    
    for ticker, info in candidates_analysis.items():
        if info is None:
            continue
        
        name = NON_HOLDING_CANDIDATES.get(ticker, {}).get('name', ticker)
        rsi = info['rsi']
        trend = info['trend']
        price = info['price']
        change_5d = info['change_5d']
        change_20d = info['change_20d']
        
        # 评估建仓可行性
        if rsi >= rsi_severe:
            buy_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '不建仓',
                'feasibility': '❌ 不推荐',
                'reason': f"RSI={rsi:.1f} 严重超买(>{rsi_severe})，5日涨{change_5d:.1f}%，追高风险极大",
                'wait_condition': f"等待RSI回落至<{new_position_rsi_max}",
                'rsi': round(rsi, 1),
                'trend': trend,
                'price': round(price, 3),
                'change_5d': round(change_5d, 2),
                'change_20d': round(change_20d, 2),
            })
        elif rsi >= rsi_overbought:
            target_price = round(price * 0.92, 3)
            buy_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '等待回调',
                'feasibility': '⚠️ 观望',
                'reason': f"RSI={rsi:.1f} 超买区，{trend}但需回调",
                'wait_condition': f"等待价格回调至{target_price}附近",
                'rsi': round(rsi, 1),
                'trend': trend,
                'price': round(price, 3),
                'change_5d': round(change_5d, 2),
                'change_20d': round(change_20d, 2),
            })
        elif rsi <= new_position_rsi_max and trend in ['上涨', '强势上涨']:
            # RSI健康且趋势向上 - 可建仓
            max_buy = min(3000, available_budget - total_buy_amount)
            shares_to_buy = int(max_buy / price / 100) * 100
            if shares_to_buy >= 100 and total_buy_amount < available_budget:
                buy_amount = shares_to_buy * price
                buy_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '可建仓',
                    'feasibility': '✅ 推荐',
                    'shares': shares_to_buy,
                    'price_range': f"{price*0.98:.3f} - {price:.3f}",
                    'amount': round(buy_amount, 2),
                    'reason': f"RSI={rsi:.1f} 健康(<{new_position_rsi_max})，{trend}",
                    'rsi': round(rsi, 1),
                    'trend': trend,
                    'price': round(price, 3),
                    'change_5d': round(change_5d, 2),
                    'change_20d': round(change_20d, 2),
                })
                total_buy_amount += buy_amount
            else:
                buy_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '可考虑',
                    'feasibility': '✅ 可建仓',
                    'reason': f"RSI={rsi:.1f} 健康，{trend}（预算已用尽或不足）",
                    'rsi': round(rsi, 1),
                    'trend': trend,
                    'price': round(price, 3),
                    'change_5d': round(change_5d, 2),
                    'change_20d': round(change_20d, 2),
                })
        elif rsi < 40:
            # 超卖区 - 可左侧布局
            max_buy = min(2000, available_budget - total_buy_amount)
            shares_to_buy = int(max_buy / price / 100) * 100
            if shares_to_buy >= 100 and total_buy_amount < available_budget:
                buy_amount = shares_to_buy * price
                buy_recommendations.append({
                    'ticker': ticker,
                    'name': name,
                    'action': '可左侧布局',
                    'feasibility': '✅ 布局',
                    'shares': shares_to_buy,
                    'price_range': f"{price*0.97:.3f} - {price:.3f}",
                    'amount': round(buy_amount, 2),
                    'reason': f"RSI={rsi:.1f} 偏低(<40)，{trend}，左侧布局",
                    'rsi': round(rsi, 1),
                    'trend': trend,
                    'price': round(price, 3),
                    'change_5d': round(change_5d, 2),
                    'change_20d': round(change_20d, 2),
                })
                total_buy_amount += buy_amount
        else:
            buy_recommendations.append({
                'ticker': ticker,
                'name': name,
                'action': '观望',
                'feasibility': '⚪ 中性',
                'reason': f"RSI={rsi:.1f}，{trend}，无明确建仓信号",
                'rsi': round(rsi, 1),
                'trend': trend,
                'price': round(price, 3),
                'change_5d': round(change_5d, 2),
                'change_20d': round(change_20d, 2),
            })
    
    return {
        'sell': sell_recommendations,
        'buy': buy_recommendations,
        'hold': hold_recommendations,
        'total_sell_amount': round(total_sell_amount, 2),
        'total_buy_amount': round(total_buy_amount, 2),
        'net_investment': round(total_buy_amount - total_sell_amount, 2),
    }


def main():
    print("=" * 60)
    print("投资组合分析 - 2026-01-14")
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
    print("\n[3/5] 复盘历史建议拟合度 (1/5, 1/7, 1/9, 1/12, 1/13)...")
    backtest_results = calculate_backtest_accuracy()
    
    # 计算复盘准确率
    correct_count = sum(1 for r in backtest_results if r['effectiveness'] == 'CORRECT')
    total_count = len(backtest_results)
    accuracy = correct_count / total_count if total_count > 0 else 0
    
    print(f"  复盘项目数量: {total_count}")
    print(f"  正确建议数量: {correct_count}")
    print(f"  复盘准确率: {accuracy*100:.1f}%")
    
    # 4. 使用调整后的风控阈值
    print("\n[4/5] 应用动态调整后的风控阈值...")
    risk_thresholds = ADJUSTED_RISK_THRESHOLDS.copy()
    risk_thresholds['backtest_accuracy'] = accuracy
    print(f"  RSI超买阈值: {risk_thresholds['rsi_overbought']}")
    print(f"  RSI严重超买阈值: {risk_thresholds['rsi_severe_overbought']}")
    print(f"  新建仓RSI上限: {risk_thresholds['new_position_rsi_max']}")
    
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
        'analysis_date': '2026-01-14',
        'account_info': ACCOUNT_INFO,
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
    
    print(f"\n账户信息:")
    print(f"  总资产: {ACCOUNT_INFO['total_assets']:.2f} 元")
    print(f"  持仓市值: {ACCOUNT_INFO['market_value']:.2f} 元")
    print(f"  可用资金: {ACCOUNT_INFO['available_cash']:.2f} 元")
    print(f"  持仓盈亏: +{ACCOUNT_INFO['total_pnl']:.2f} 元")
    
    print(f"\n风控阈值:")
    print(f"  RSI超买: {risk_thresholds['rsi_overbought']}")
    print(f"  RSI严重超买: {risk_thresholds['rsi_severe_overbought']}")
    print(f"  复盘准确率: {accuracy*100:.1f}%")
    
    print(f"\n操作建议:")
    print(f"  减仓建议: {len(recommendations['sell'])} 项，预计回笼 {recommendations['total_sell_amount']:.0f} 元")
    print(f"  建仓建议: {len([b for b in recommendations['buy'] if b.get('shares')])} 项，预计支出 {recommendations['total_buy_amount']:.0f} 元")
    print(f"  持仓留存: {len(recommendations['hold'])} 项")
    print(f"  净增投资: {recommendations['net_investment']:.0f} 元")
    
    if recommendations['net_investment'] <= 10000:
        print(f"\n✅ 符合增量资金限制 (≤ 10,000 元)")
    else:
        print(f"\n⚠️ 超出增量资金限制！需调整建议")
    
    return result


if __name__ == '__main__':
    result = main()

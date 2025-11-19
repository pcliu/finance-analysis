#!/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
# -*- coding: utf-8 -*-

import sys
import os

# Add the skill directory to Python path
sys.path.append('quantitative-trading-skills/quantitative-trading')
import pandas as pd
from datetime import datetime, timedelta

# Import the data fetcher module
try:
    from api.data_fetcher import fetch_stock_data, fetch_multiple_stocks
    print("✓ Successfully imported data fetcher modules")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you're using the finance-analysis environment")
    sys.exit(1)

def fetch_688981_data():
    """
    获取688981.SH（中芯国际）的近期股票价格数据
    """
    print("\n" + "="*60)
    print("开始获取688981.SH股票数据...")
    print("="*60)

    ticker = "688981.SS"  # 使用.SS后缀表示上交所科创板
    periods = ["1mo", "3mo", "6mo", "1y"]

    results = {}

    for period in periods:
        print(f"\n正在获取{period}的数据...")
        try:
            data = fetch_stock_data(ticker, period=period)

            if data is not None and not data.empty:
                print(f"✓ 成功获取{period}数据")
                print(f"  数据范围: {data.index[0].date()} 至 {data.index[-1].date()}")
                print(f"  记录数: {len(data)}个交易日")
                print(f"  最新价格: ¥{data['Close'].iloc[-1]:.2f}")
                print(f"  区间涨幅: {((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100:.2f}%")

                # 显示最近5天的数据
                print(f"\n  最近5个交易日数据:")
                recent = data.tail(5)
                for idx, row in recent.iterrows():
                    print(f"    {idx.date()}: ¥{row['Close']:.2f} (涨跌: {row['Close']-row['Open']:+.2f}, 成交量: {row['Volume']:,})")

                results[period] = data
            else:
                print(f"✗ 无法获取{period}的数据")
                results[period] = None

        except Exception as e:
            print(f"✗ 获取{period}数据时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            results[period] = None

    # 获取详细信息（使用1年的数据）
    print("\n" + "="*60)
    print("详细分析（基于1年数据）")
    print("="*60)

    if results.get("1y") is not None:
        data_1y = results["1y"]

        # 基本统计
        print(f"\n1. 价格统计:")
        print(f"   - 当前价格: ¥{data_1y['Close'].iloc[-1]:.2f}")
        print(f"   - 最高价格: ¥{data_1y['High'].max():.2f}")
        print(f"   - 最低价格: ¥{data_1y['Low'].min():.2f}")
        print(f"   - 平均价格: ¥{data_1y['Close'].mean():.2f}")

        # 收益率
        returns = data_1y['Close'].pct_change().dropna()
        print(f"\n2. 收益率统计:")
        print(f"   - 日收益率(平均): {returns.mean()*100:.3f}%")
        print(f"   - 日收益率(标准差): {returns.std()*100:.3f}%")
        print(f"   - 年化收益率: {(1 + returns.mean())**252 - 1:.2%}")
        print(f"   - 年化波动率: {returns.std() * (252**0.5):.2%}")

        # 近期表现
        recent_30d = data_1y.tail(30)
        recent_7d = data_1y.tail(7)

        print(f"\n3. 近期表现:")
        print(f"   - 近7日涨跌幅: {((recent_7d['Close'].iloc[-1] / recent_7d['Close'].iloc[0]) - 1) * 100:.2f}%")
        print(f"   - 近30日涨跌幅: {((recent_30d['Close'].iloc[-1] / recent_30d['Close'].iloc[0]) - 1) * 100:.2f}%")

        # 保存数据到文件
        output_dir = "workspace"
        os.makedirs(output_dir, exist_ok=True)

        # 保存CSV
        csv_path = os.path.join(output_dir, "688981_stock_data.csv")
        data_1y.to_csv(csv_path, encoding='utf-8-sig')
        print(f"\n✓ 数据已保存至: {csv_path}")

        # 保存近期数据（30天）
        recent_path = os.path.join(output_dir, "688981_recent_30d.csv")
        recent_30d.to_csv(recent_path, encoding='utf-8-sig')
        print(f"✓ 近期数据已保存至: {recent_path}")

        return results
    else:
        print("✗ 无法获取1年数据，无法生成详细分析")
        return None

if __name__ == "__main__":
    fetch_688981_data()

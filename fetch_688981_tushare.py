#!/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
# -*- coding: utf-8 -*-

import sys
import os

# Add the skill directory to Python path
sys.path.append('quantitative-trading-skills/quantitative-trading')

import pandas as pd
from datetime import datetime, timedelta

try:
    import tushare as ts
    print("✓ Successfully imported tushare")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Make sure you're using the finance-analysis environment")
    sys.exit(1)

# 设置tushare token（如果环境变量中没有设置）
if not os.getenv('TUSHARE_TOKEN'):
    print("⚠️  警告: 未设置TUSHARE_TOKEN环境变量")
    print("   如需获取token，请访问: https://tushare.pro/register")
    print("   然后设置环境变量: export TUSHARE_TOKEN='your_token'")
    print("   尝试使用yfinance作为备用方案...\n")

print("\n" + "="*60)
print("使用tushare获取688981.SH（中芯国际）股票数据")
print("="*60)

def get_tushare_token():
    """获取tushare token"""
    token = os.getenv('TUSHARE_TOKEN')
    if token:
        return token

    # 尝试从配置文件读取
    config_paths = [
        os.path.expanduser('~/.tushare_token'),
        './.tushare_token',
        './tushare_token.txt'
    ]

    for path in config_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    return f.read().strip()
            except:
                pass

    return None

def fetch_with_tushare():
    """使用tushare获取数据"""
    token = get_tushare_token()

    if not token:
        print("✗ 无法获取tushare token")
        print("\n请按以下步骤操作:")
        print("1. 访问 https://tushare.pro/register 注册账号")
        print("2. 在个人中心获取token")
        print("3. 设置环境变量: export TUSHARE_TOKEN='your_token'")
        print("   或者创建文件 ~/.tushare_token 并写入token")
        return False

    try:
        print(f"\n正在初始化tushare...")
        pro = ts.pro_api(token)

        # 获取688981.SH的数据
        ticker = "688981.SH"
        print(f"\n正在获取{ticker}的数据...")

        # 获取最近1年的日线数据
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')

        df = pro.daily(
            ts_code=ticker,
            start_date=start_date,
            end_date=end_date,
            fields='ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount'
        )

        if df is not None and not df.empty:
            print(f"✓ 成功获取数据!")
            print(f"  记录数: {len(df)}个交易日")

            # 按日期排序（从过去到现在）
            df = df.sort_values('trade_date').reset_index(drop=True)

            # 转换日期格式
            df['trade_date'] = pd.to_datetime(df['trade_date'])

            # 显示最近5天的数据
            print(f"\n最近5个交易日数据:")
            recent = df.tail(5)
            for idx, row in recent.iterrows():
                print(f"  {row['trade_date'].date()}: ¥{row['close']:.2f} "
                      f"(涨跌: {row['change']:+.2f}, "
                      f"涨跌幅: {row['pct_chg']:+.2f}%, "
                      f"成交量: {row['vol']:,})")

            # 统计分析
            print("\n" + "="*60)
            print("详细分析（基于1年数据）")
            print("="*60)

            # 基本统计
            print(f"\n1. 价格统计:")
            print(f"   - 当前价格: ¥{df['close'].iloc[-1]:.2f}")
            print(f"   - 最高价格: ¥{df['high'].max():.2f}")
            print(f"   - 最低价格: ¥{df['low'].min():.2f}")
            print(f"   - 平均价格: ¥{df['close'].mean():.2f}")

            # 计算收益率
            df['returns'] = df['close'].pct_change()
            returns = df['returns'].dropna()

            print(f"\n2. 收益率统计:")
            print(f"   - 日收益率(平均): {returns.mean()*100:.3f}%")
            print(f"   - 日收益率(标准差): {returns.std()*100:.3f}%")
            print(f"   - 年化收益率: {(1 + returns.mean())**252 - 1:.2%}")
            print(f"   - 年化波动率: {returns.std() * (252**0.5):.2%}")

            # 近期表现
            recent_30d = df.tail(30)
            recent_7d = df.tail(7)

            print(f"\n3. 近期表现:")
            print(f"   - 近7日涨跌幅: {((recent_7d['close'].iloc[-1] / recent_7d['close'].iloc[0]) - 1) * 100:.2f}%")
            print(f"   - 近30日涨跌幅: {((recent_30d['close'].iloc[-1] / recent_30d['close'].iloc[0]) - 1) * 100:.2f}%")

            # 计算移动平均线
            df['MA_5'] = df['close'].rolling(window=5).mean()
            df['MA_20'] = df['close'].rolling(window=20).mean()
            df['MA_60'] = df['close'].rolling(window=60).mean()

            print(f"\n4. 移动平均线:")
            print(f"   - MA_5:  ¥{df['MA_5'].iloc[-1]:.2f}")
            print(f"   - MA_20: ¥{df['MA_20'].iloc[-1]:.2f}")
            print(f"   - MA_60: ¥{df['MA_60'].iloc[-1]:.2f}")

            # 保存数据
            output_dir = "workspace"
            os.makedirs(output_dir, exist_ok=True)

            # 保存完整数据
            csv_path = os.path.join(output_dir, "688981_tushare_data.csv")
            df.to_csv(csv_path, index=False, encoding='utf-8-sig')
            print(f"\n✓ 完整数据已保存至: {csv_path}")

            # 保存近期数据（30天）
            recent_path = os.path.join(output_dir, "688981_tushare_recent_30d.csv")
            recent_30d.to_csv(recent_path, index=False, encoding='utf-8-sig')
            print(f"✓ 近期数据已保存至: {recent_path}")

            # 保存统计摘要
            summary = {
                'ticker': ticker,
                'current_price': float(df['close'].iloc[-1]),
                'high_price': float(df['high'].max()),
                'low_price': float(df['low'].min()),
                'avg_price': float(df['close'].mean()),
                'return_7d': float(((recent_7d['close'].iloc[-1] / recent_7d['close'].iloc[0]) - 1) * 100),
                'return_30d': float(((recent_30d['close'].iloc[-1] / recent_30d['close'].iloc[0]) - 1) * 100),
                'volatility_annual': float(returns.std() * (252**0.5) * 100),
                'data_points': len(df)
            }

            summary_path = os.path.join(output_dir, "688981_summary.json")
            import json
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
            print(f"✓ 统计摘要已保存至: {summary_path}")

            return df
        else:
            print(f"✗ 无法获取股票数据")
            return None

    except Exception as e:
        print(f"✗ 获取数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    success = fetch_with_tushare()

    if not success:
        print("\n" + "="*60)
        print("备选方案: 使用yahoofinance")
        print("="*60)
        print("\n请尝试使用已安装的quantitative-trading API:")
        print("\n示例代码:")
        print("""
import sys
sys.path.append('quantitative-trading-skills/quantitative-trading')
from api.data_fetcher import fetch_stock_data

# 使用SS后缀表示上交所
data = fetch_stock_data('688981.SS', period='1y')
        """)

#!/usr/bin/env python3
"""
Trading Strategies Implementation for Quantitative Trading
Implements various trading strategies with signal generation
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import argparse
from data_fetcher import DataFetcher
from indicators import TechnicalIndicators

class TradingStrategy:
    def __init__(self, initial_capital=100000):
        self.initial_capital = initial_capital
        self.indicators = TechnicalIndicators()

    def moving_average_crossover(self, data, fast_window=20, slow_window=50):
        """
        Moving Average Crossover Strategy

        Buy when fast MA crosses above slow MA
        Sell when fast MA crosses below slow MA
        """
        # Calculate moving averages
        data['MA_Fast'] = self.indicators.calculate_sma(data, fast_window)
        data['MA_Slow'] = self.indicators.calculate_sma(data, slow_window)

        # Generate signals
        data['Signal'] = 0
        data.loc[data['MA_Fast'] > data['MA_Slow'], 'Signal'] = 1
        data.loc[data['MA_Fast'] < data['MA_Slow'], 'Signal'] = -1

        # Identify crossovers
        data['Position'] = data['Signal'].diff()
        data['Buy_Signal'] = data['Position'] == 2
        data['Sell_Signal'] = data['Position'] == -2

        return data

    def rsi_mean_reversion(self, data, rsi_window=14, oversold=30, overbought=70):
        """
        RSI Mean Reversion Strategy

        Buy when RSI crosses above oversold level
        Sell when RSI crosses below overbought level
        """
        # Calculate RSI
        data['RSI'] = self.indicators.calculate_rsi(data, rsi_window)

        # Generate signals
        data['Signal'] = 0
        data.loc[data['RSI'] < oversold, 'Signal'] = 1  # Oversold - Buy signal
        data.loc[data['RSI'] > overbought, 'Signal'] = -1  # Overbought - Sell signal

        # Track previous RSI for crossover detection
        data['RSI_Prev'] = data['RSI'].shift(1)

        # Generate crossover signals
        data['Buy_Signal'] = (data['RSI'] > oversold) & (data['RSI_Prev'] <= oversold)
        data['Sell_Signal'] = (data['RSI'] < overbought) & (data['RSI_Prev'] >= overbought)

        return data

    def bollinger_bands_strategy(self, data, window=20, num_std=2):
        """
        Bollinger Bands Strategy

        Buy when price touches lower band
        Sell when price touches upper band
        """
        # Calculate Bollinger Bands
        bb = self.indicators.calculate_bollinger_bands(data, window, num_std)
        data['BB_Upper'] = bb['Upper']
        data['BB_Middle'] = bb['Middle']
        data['BB_Lower'] = bb['Lower']

        # Generate signals based on band touches
        data['Buy_Signal'] = data['Close'] <= data['BB_Lower']
        data['Sell_Signal'] = data['Close'] >= data['BB_Upper']

        # Optional: Add confirmation with middle band
        data['Position'] = 0
        data.loc[data['Close'] > data['BB_Middle'], 'Position'] = 1
        data.loc[data['Close'] < data['BB_Middle'], 'Position'] = -1

        return data

    def macd_strategy(self, data, fast=12, slow=26, signal=9):
        """
        MACD Strategy

        Buy when MACD crosses above signal line
        Sell when MACD crosses below signal line
        """
        # Calculate MACD
        macd = self.indicators.calculate_macd(data, fast, slow, signal)
        data['MACD'] = macd['MACD']
        data['MACD_Signal'] = macd['Signal']
        data['MACD_Histogram'] = macd['Histogram']

        # Generate signals based on MACD/Signal crossover
        data['Buy_Signal'] = (data['MACD'] > data['MACD_Signal']) & (data['MACD'].shift(1) <= data['MACD_Signal'].shift(1))
        data['Sell_Signal'] = (data['MACD'] < data['MACD_Signal']) & (data['MACD'].shift(1) >= data['MACD_Signal'].shift(1))

        # Additional signal based on histogram
        data['Histogram_Signal'] = 0
        data.loc[data['MACD_Histogram'] > 0, 'Histogram_Signal'] = 1
        data.loc[data['MACD_Histogram'] < 0, 'Histogram_Signal'] = -1

        return data

    def stochastic_oscillator_strategy(self, data, k_window=14, d_window=3, oversold=20, overbought=80):
        """
        Stochastic Oscillator Strategy

        Buy when %K crosses above %D in oversold territory
        Sell when %K crosses below %D in overbought territory
        """
        # Calculate Stochastic Oscillator
        stoch = self.indicators.calculate_stochastic(data, k_window, d_window)
        data['Stoch_K'] = stoch['K']
        data['Stoch_D'] = stoch['D']

        # Generate signals
        data['Buy_Signal'] = ((data['Stoch_K'] > data['Stoch_D']) &
                            (data['Stoch_K'].shift(1) <= data['Stoch_D'].shift(1)) &
                            (data['Stoch_K'] < oversold))

        data['Sell_Signal'] = ((data['Stoch_K'] < data['Stoch_D']) &
                             (data['Stoch_K'].shift(1) >= data['Stoch_D'].shift(1)) &
                             (data['Stoch_K'] > overbought))

        return data

    def momentum_breakout(self, data, lookback_period=20, volume_threshold=1.5):
        """
        Momentum Breakout Strategy

        Buy when price breaks above recent high with increased volume
        Sell when price breaks below recent low with increased volume
        """
        # Calculate recent highs and lows
        data['High_Lookback'] = data['High'].rolling(window=lookback_period).max()
        data['Low_Lookback'] = data['Low'].rolling(window=lookback_period).min()
        data['Avg_Volume'] = data['Volume'].rolling(window=lookback_period).mean()

        # Generate breakout signals
        data['Breakout_Up'] = (data['Close'] > data['High_Lookback'].shift(1)) & (data['Volume'] > volume_threshold * data['Avg_Volume'])
        data['Breakout_Down'] = (data['Close'] < data['Low_Lookback'].shift(1)) & (data['Volume'] > volume_threshold * data['Avg_Volume'])

        data['Buy_Signal'] = data['Breakout_Up']
        data['Sell_Signal'] = data['Breakout_Down']

        return data

    def mean_reversion_strategy(self, data, lookback_period=20, entry_threshold=2.0, exit_threshold=0.5):
        """
        Mean Reversion Strategy

        Buy when price is significantly below mean
        Sell when price returns to mean
        """
        # Calculate mean and standard deviation
        data['Mean'] = data['Close'].rolling(window=lookback_period).mean()
        data['Std'] = data['Close'].rolling(window=lookback_period).std()

        # Calculate Z-score
        data['Z_Score'] = (data['Close'] - data['Mean']) / data['Std']

        # Generate signals
        data['Buy_Signal'] = data['Z_Score'] < -entry_threshold
        data['Sell_Signal'] = data['Z_Score'] > entry_threshold
        data['Exit_Long'] = (data['Z_Score'] > -exit_threshold) & (data['Z_Score'] < exit_threshold)

        return data

    def dual_momentum_strategy(self, data, stock_data_market, lookback_period=12):
        """
        Dual Momentum Strategy

        Combines absolute and relative momentum
        """
        # Calculate returns for both assets
        data['Stock_Returns'] = data['Close'].pct_change(lookback_period)
        data['Market_Returns'] = stock_data_market['Close'].pct_change(lookback_period)

        # Calculate relative momentum
        data['Relative_Momentum'] = data['Stock_Returns'] - data['Market_Returns']

        # Generate signals
        data['Absolute_Momentum_Signal'] = data['Stock_Returns'] > 0
        data['Relative_Momentum_Signal'] = data['Relative_Momentum'] > 0

        # Buy only when both momentums are positive
        data['Buy_Signal'] = data['Absolute_Momentum_Signal'] & data['Relative_Momentum_Signal']
        data['Sell_Signal'] = ~data['Buy_Signal']

        return data

    def pair_trading_strategy(self, data1, data2, lookback_period=60, entry_threshold=2.0, exit_threshold=0.5):
        """
        Pair Trading Strategy

        Trade based on mean reversion of price ratio between two stocks
        """
        # Calculate price ratio
        ratio = data1['Close'] / data2['Close']

        # Calculate mean and standard deviation of ratio
        ratio_mean = ratio.rolling(window=lookback_period).mean()
        ratio_std = ratio.rolling(window=lookback_period).std()

        # Calculate Z-score of ratio
        ratio_zscore = (ratio - ratio_mean) / ratio_std

        # Generate signals
        signals = pd.DataFrame(index=ratio.index)
        signals['Ratio'] = ratio
        signals['Ratio_ZScore'] = ratio_zscore
        signals['Ratio_Mean'] = ratio_mean

        # Pair trading signals
        signals['Buy_Stock1_Sell_Stock2'] = ratio_zscore < -entry_threshold  # Ratio is low, buy stock1, sell stock2
        signals['Sell_Stock1_Buy_Stock2'] = ratio_zscore > entry_threshold   # Ratio is high, sell stock1, buy stock2
        signals['Exit_Position'] = abs(ratio_zscore) < exit_threshold

        return signals

    def volatility_targeting_strategy(self, data, target_volatility=0.15, lookback_period=20):
        """
        Volatility Targeting Strategy

        Adjust position size based on volatility
        """
        # Calculate realized volatility
        data['Realized_Vol'] = data['Close'].pct_change().rolling(window=lookback_period).std() * np.sqrt(252)

        # Calculate target position size
        data['Target_Position'] = target_volatility / data['Realized_Vol']

        # Cap position size (maximum 2x leverage, minimum 0)
        data['Position_Size'] = data['Target_Position'].clip(0, 2)

        # Generate trend signals (simple momentum)
        data['Price_Momentum'] = data['Close'] > data['Close'].rolling(window=lookback_period).mean()
        data['Position'] = data['Position_Size'] * data['Price_Momentum']

        return data

    def multi_strategy_signals(self, data, strategies=None):
        """
        Combine multiple strategies for more robust signals
        """
        if strategies is None:
            strategies = ['ma_crossover', 'rsi', 'macd', 'bollinger']

        signals_data = data.copy()

        if 'ma_crossover' in strategies:
            ma_data = self.moving_average_crossover(data.copy())
            signals_data['MA_Signal'] = ma_data['Position']

        if 'rsi' in strategies:
            rsi_data = self.rsi_mean_reversion(data.copy())
            signals_data['RSI_Signal'] = np.where(rsi_data['Buy_Signal'], 1,
                                                 np.where(rsi_data['Sell_Signal'], -1, 0))

        if 'macd' in strategies:
            macd_data = self.macd_strategy(data.copy())
            signals_data['MACD_Signal'] = np.where(macd_data['Buy_Signal'], 1,
                                                  np.where(macd_data['Sell_Signal'], -1, 0))

        if 'bollinger' in strategies:
            bb_data = self.bollinger_bands_strategy(data.copy())
            signals_data['BB_Signal'] = np.where(bb_data['Buy_Signal'], 1,
                                                np.where(bb_data['Sell_Signal'], -1, 0))

        # Calculate consensus signal
        signal_columns = [col for col in signals_data.columns if col.endswith('_Signal')]
        if signal_columns:
            signals_data['Consensus_Signal'] = signals_data[signal_columns].mean(axis=1)
            signals_data['Final_Signal'] = np.where(signals_data['Consensus_Signal'] > 0.5, 1,
                                                   np.where(signals_data['Consensus_Signal'] < -0.5, -1, 0))

        return signals_data

    def get_strategy_signals(self, data, strategy_name, **kwargs):
        """
        Get signals for a specific strategy
        """
        strategy_map = {
            'ma_crossover': self.moving_average_crossover,
            'rsi': self.rsi_mean_reversion,
            'macd': self.macd_strategy,
            'bollinger': self.bollinger_bands_strategy,
            'stochastic': self.stochastic_oscillator_strategy,
            'momentum': self.momentum_breakout,
            'mean_reversion': self.mean_reversion_strategy,
            'volatility_targeting': self.volatility_targeting_strategy
        }

        if strategy_name not in strategy_map:
            raise ValueError(f"Strategy '{strategy_name}' not found")

        return strategy_map[strategy_name](data, **kwargs)


def main():
    parser = argparse.ArgumentParser(description='Generate trading strategy signals')
    parser.add_argument('--ticker', '-t', type=str, required=True, help='Stock ticker')
    parser.add_argument('--strategy', '-s', type=str, required=True,
                       choices=['ma_crossover', 'rsi', 'macd', 'bollinger', 'stochastic',
                               'momentum', 'mean_reversion', 'multi'],
                       help='Trading strategy to use')
    parser.add_argument('--period', type=str, default='1y', help='Period for data')
    parser.add_argument('--market-ticker', type=str, help='Market ticker for relative strategies')
    parser.add_argument('--pair-ticker', type=str, help='Second ticker for pair trading')
    parser.add_argument('--output', type=str, help='Output file path')
    parser.add_argument('--plot', action='store_true', help='Plot results')

    args = parser.parse_args()

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(args.ticker, period=args.period)

    if data is None:
        print(f"Could not fetch data for {args.ticker}")
        return

    strategy = TradingStrategy()

    try:
        if args.strategy == 'multi':
            result_data = strategy.multi_strategy_signals(data)
        elif args.strategy == 'pair_trading' and args.pair_ticker:
            pair_data = fetcher.fetch_stock_data(args.pair_ticker, period=args.period)
            if pair_data is not None:
                result_data = strategy.pair_trading_strategy(data, pair_data)
            else:
                print(f"Could not fetch data for pair ticker {args.pair_ticker}")
                return
        else:
            result_data = strategy.get_strategy_signals(data, args.strategy)

        print(f"Generated signals for {args.strategy} strategy on {args.ticker}")

        # Display recent signals
        signal_cols = [col for col in result_data.columns if 'Signal' in col or 'Position' in col]
        if signal_cols:
            print(f"\nRecent signals:")
            print(result_data[signal_cols].tail(10))

        # Save results
        if args.output:
            result_data.to_csv(args.output)
            print(f"Results saved to {args.output}")

        # Plot results
        if args.plot:
            plt.figure(figsize=(12, 8))
            plt.subplot(2, 1, 1)
            plt.plot(result_data.index, result_data['Close'], label='Close Price')

            if 'MA_Fast' in result_data.columns:
                plt.plot(result_data.index, result_data['MA_Fast'], label='Fast MA')
            if 'MA_Slow' in result_data.columns:
                plt.plot(result_data.index, result_data['MA_Slow'], label='Slow MA')

            buy_signals = result_data[result_data['Buy_Signal'] == True]
            sell_signals = result_data[result_data['Sell_Signal'] == True]

            plt.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', s=100, label='Buy')
            plt.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', s=100, label='Sell')

            plt.legend()
            plt.title(f'{args.ticker} - {args.strategy} Strategy')
            plt.show()

    except Exception as e:
        print(f"Error generating strategy signals: {e}")


if __name__ == "__main__":
    main()
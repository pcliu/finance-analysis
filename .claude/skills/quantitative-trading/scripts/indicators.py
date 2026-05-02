#!/usr/bin/env python3
"""
Technical Indicators Calculator for Quantitative Trading
Calculates various technical indicators for stock analysis
"""

import pandas as pd
import numpy as np
import argparse
import sys

try:
    from .data_fetcher import DataFetcher
except ImportError:
    from data_fetcher import DataFetcher

class TechnicalIndicators:
    def __init__(self):
        pass

    # Trend Indicators
    def calculate_sma(self, data: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.DataFrame:
        """Calculate Simple Moving Average"""
        return data[column].rolling(window=window).mean().to_frame(name='SMA')

    def calculate_ema(self, data: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.DataFrame:
        """Calculate Exponential Moving Average.
        
        Args:
            data: DataFrame with price data
            window: EMA period
            column: Column to calculate EMA on
        """
        return data[column].ewm(span=window).mean().to_frame(name='EMA')

    def calculate_wma(self, data: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.DataFrame:
        """Calculate Weighted Moving Average"""
        weights = np.arange(1, window + 1)
        wma = data[column].rolling(window=window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)
        return wma.to_frame(name='WMA')

    def calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20, num_std: int = 2, column: str = 'Close') -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        sma = data[column].rolling(window=window).mean()
        std = data[column].rolling(window=window).std()

        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        bandwidth = (upper_band - lower_band) / sma
        percent_b = (data[column] - lower_band) / (upper_band - lower_band)

        return pd.DataFrame({
            'Middle': sma,
            'Upper': upper_band,
            'Lower': lower_band,
            'Bandwidth': bandwidth,
            'Percent_B': percent_b
        })

    def calculate_adx(self, data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """Calculate Average Directional Index"""
        high = data['High']
        low = data['Low']
        close = data['Close']

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.DataFrame([tr1, tr2, tr3]).max()

        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low

        pos_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        neg_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)

        # Smoothed values
        atr = tr.rolling(window=window).mean()
        pos_di = 100 * (pd.Series(pos_dm).rolling(window=window).mean() / atr)
        neg_di = 100 * (pd.Series(neg_dm).rolling(window=window).mean() / atr)

        # ADX
        dx = 100 * abs(pos_di - neg_di) / (pos_di + neg_di)
        adx = dx.rolling(window=window).mean()

        return adx.to_frame(name='ADX')

    # Momentum Indicators
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14, column: str = 'Close') -> pd.DataFrame:
        """
        Calculate Relative Strength Index using Wilder's Smoothing
        """
        delta = data[column].diff()
        
        # Wilder's Smoothing uses EMA with alpha = 1/window (or com = window - 1)
        # Standard RSI definition
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.ewm(com=window - 1, min_periods=window).mean()
        avg_loss = loss.ewm(com=window - 1, min_periods=window).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.to_frame(name='RSI')

    def calculate_stochastic(self, data: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> pd.DataFrame:
        """Calculate Stochastic Oscillator"""
        high_max = data['High'].rolling(window=k_window).max()
        low_min = data['Low'].rolling(window=k_window).min()

        percent_k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        percent_d = percent_k.rolling(window=d_window).mean()

        return pd.DataFrame({
            'K': percent_k,
            'D': percent_d
        })

    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, column: str = 'Close') -> pd.DataFrame:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = data[column].ewm(span=fast).mean()
        ema_slow = data[column].ewm(span=slow).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return pd.DataFrame({
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        })

    def calculate_williams_r(self, data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """Calculate Williams %R"""
        high_max = data['High'].rolling(window=window).max()
        low_min = data['Low'].rolling(window=window).min()

        williams_r = -100 * ((high_max - data['Close']) / (high_max - low_min))

        return williams_r.to_frame(name='Williams_R')

    def calculate_cci(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Calculate Commodity Channel Index"""
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        sma_tp = tp.rolling(window=window).mean()
        mad = tp.rolling(window=window).apply(lambda x: np.abs(x - x.mean()).mean())

        cci = (tp - sma_tp) / (0.015 * mad)

        return cci.to_frame(name='CCI')

    # Volatility Indicators
    def calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
        """Calculate Average True Range"""
        high = data['High']
        low = data['Low']
        close = data['Close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.DataFrame([tr1, tr2, tr3]).max()
        atr = tr.rolling(window=window).mean()

        return atr.to_frame(name='ATR')

    def calculate_keltner_channels(self, data: pd.DataFrame, window: int = 20, multiplier: int = 2) -> pd.DataFrame:
        """Calculate Keltner Channels"""
        ema = self.calculate_ema(data, window=window)['EMA']
        atr = self.calculate_atr(data, window)['ATR']

        upper_channel = ema + (multiplier * atr)
        lower_channel = ema - (multiplier * atr)

        return pd.DataFrame({
            'Middle': ema,
            'Upper': upper_channel,
            'Lower': lower_channel
        })

    # Volume Indicators
    def calculate_obv(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate On-Balance Volume"""
        obv = np.where(data['Close'] > data['Close'].shift(), data['Volume'],
                      np.where(data['Close'] < data['Close'].shift(), -data['Volume'], 0)).cumsum()
        return pd.DataFrame({'OBV': obv}, index=data.index)

    def calculate_volume_sma(self, data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
        """Calculate Volume Simple Moving Average"""
        return data['Volume'].rolling(window=window).mean().to_frame(name='Volume_SMA')

    def calculate_volume_profile(self, data: pd.DataFrame, bins: int = 50) -> pd.DataFrame:
        """Calculate Volume Profile. Note: This does NOT return time-series data."""
        price_range = np.linspace(data['Low'].min(), data['High'].max(), bins)
        volume_profile = []

        for i in range(len(price_range) - 1):
            mask = ((data['Close'] >= price_range[i]) &
                   (data['Close'] < price_range[i + 1]))
            volume_profile.append(data.loc[mask, 'Volume'].sum())
        
        # Return a DataFrame with Price and Volume (not time-indexed)
        return pd.DataFrame({
            'Price': price_range[:-1], 
            'Volume': volume_profile
        })

    # Support and Resistance Levels
    def calculate_pivot_points(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate Pivot Points"""
        prev_high = data['High'].shift(1)
        prev_low = data['Low'].shift(1)
        prev_close = data['Close'].shift(1)

        pivot = (prev_high + prev_low + prev_close) / 3
        support1 = (2 * pivot) - prev_high
        support2 = pivot - (prev_high - prev_low)
        resistance1 = (2 * pivot) - prev_low
        resistance2 = pivot + (prev_high - prev_low)

        return pd.DataFrame({
            'Pivot': pivot,
            'Support1': support1,
            'Support2': support2,
            'Resistance1': resistance1,
            'Resistance2': resistance2
        })

    def calculate_fibonacci_retracements(self, data: pd.DataFrame, trend: str = 'up') -> pd.DataFrame:
        """Calculate Fibonacci Retracement Levels.
        Returns a DataFrame with constant values for the calculated period.
        """
        if trend == 'up':
            swing_low = data['Low'].min()
            swing_high = data['High'].max()
        else:
            swing_high = data['High'].max()
            swing_low = data['Low'].min()

        diff = swing_high - swing_low
        
        # Create a dict of values
        levels = {
            '0%': swing_high,
            '23.6%': swing_high - 0.236 * diff,
            '38.2%': swing_high - 0.382 * diff,
            '50%': swing_high - 0.5 * diff,
            '61.8%': swing_high - 0.618 * diff,
            '78.6%': swing_high - 0.786 * diff,
            '100%': swing_low
        }
        
        # Broadcast to DataFrame matching input index
        return pd.DataFrame(levels, index=data.index)

    def calculate_all_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all commonly used indicators and return a single DataFrame."""
        
        # Dictionary to collect all indicator DataFrames
        frames = []

        # Trend indicators
        frames.append(self.calculate_sma(data, 20).rename(columns={'SMA': 'SMA_20'}))
        frames.append(self.calculate_sma(data, 50).rename(columns={'SMA': 'SMA_50'}))
        frames.append(self.calculate_sma(data, 200).rename(columns={'SMA': 'SMA_200'}))
        frames.append(self.calculate_ema(data, 12).rename(columns={'EMA': 'EMA_12'}))
        frames.append(self.calculate_ema(data, 26).rename(columns={'EMA': 'EMA_26'}))

        frames.append(self.calculate_bollinger_bands(data).add_prefix('BB_'))

        # Momentum indicators
        frames.append(self.calculate_rsi(data))
        frames.append(self.calculate_williams_r(data))
        frames.append(self.calculate_cci(data))

        frames.append(self.calculate_macd(data).add_prefix('MACD_'))

        frames.append(self.calculate_stochastic(data).add_prefix('Stoch_'))

        # Volatility indicators
        frames.append(self.calculate_atr(data))

        frames.append(self.calculate_keltner_channels(data).add_prefix('Keltner_'))

        # Volume indicators
        frames.append(self.calculate_obv(data))
        frames.append(self.calculate_volume_sma(data))

        # Join all frames
        result = pd.concat(frames, axis=1)
        
        return result


def main():
    parser = argparse.ArgumentParser(description='Calculate technical indicators')
    parser.add_argument('--ticker', '-t', type=str, required=True, help='Ticker symbol')
    parser.add_argument('--indicators', type=str, help='Comma-separated list of indicators')
    parser.add_argument('--period', type=str, default='1y', help='Period for data fetching')
    parser.add_argument('--all', action='store_true', help='Calculate all indicators')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Fetch data
    fetcher = DataFetcher()
    data = fetcher.fetch_stock_data(args.ticker, period=args.period)

    if data is None:
        print(f"Could not fetch data for {args.ticker}")
        return

    # Calculate indicators
    tech_indicators = TechnicalIndicators()
    
    final_df = data.copy()

    if args.all:
        indicators_df = tech_indicators.calculate_all_indicators(data)
        final_df = final_df.join(indicators_df)
        print(f"Calculated {len(indicators_df.columns)} indicators for {args.ticker}")
    elif args.indicators:
        indicator_list = [i.strip() for i in args.indicators.split(',')]

        for ind in indicator_list:
            if hasattr(tech_indicators, f'calculate_{ind.lower()}'):
                try:
                    result = getattr(tech_indicators, f'calculate_{ind.lower()}')(data)
                    # Join with prefix if it's a generic name like 'K', 'D' to avoid collisions if multiple stochs? 
                    # Actually result is a DataFrame, just join it.
                    final_df = final_df.join(result, rsuffix=f'_{ind}')
                    print(f"Calculated {ind}")
                except Exception as e:
                    print(f"Error calculating {ind}: {e}")
            else:
                print(f"Indicator {ind} not found")
    else:
        print("Please specify either --all or --indicators")
        return

    # Save or display results
    if args.output:
        final_df.to_csv(args.output)
        print(f"Results saved to {args.output}")
    else:
        print(f"\nRecent indicator values for {args.ticker}:")
        print(final_df.tail(10).round(2))


if __name__ == "__main__":
    main()
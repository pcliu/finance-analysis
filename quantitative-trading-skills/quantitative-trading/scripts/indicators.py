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
    def calculate_sma(self, data: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.Series:
        """Calculate Simple Moving Average"""
        return data[column].rolling(window=window).mean()

    def calculate_ema(self, data: pd.DataFrame, span: int = 20, column: str = 'Close') -> pd.Series:
        """Calculate Exponential Moving Average"""
        return data[column].ewm(span=span).mean()

    def calculate_wma(self, data: pd.DataFrame, window: int = 20, column: str = 'Close') -> pd.Series:
        """Calculate Weighted Moving Average"""
        weights = np.arange(1, window + 1)
        return data[column].rolling(window=window).apply(lambda x: np.dot(x, weights) / weights.sum(), raw=True)

    def calculate_bollinger_bands(self, data: pd.DataFrame, window: int = 20, num_std: int = 2, column: str = 'Close') -> dict:
        """Calculate Bollinger Bands"""
        sma = self.calculate_sma(data, window, column)
        std = data[column].rolling(window=window).std()

        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)

        return {
            'Middle': sma,
            'Upper': upper_band,
            'Lower': lower_band,
            'Bandwidth': (upper_band - lower_band) / sma,
            'Percent_B': (data[column] - lower_band) / (upper_band - lower_band)
        }

    def calculate_adx(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
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

        return adx

    # Momentum Indicators
    def calculate_rsi(self, data: pd.DataFrame, window: int = 14, column: str = 'Close') -> pd.Series:
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
        
        return rsi

    def calculate_stochastic(self, data: pd.DataFrame, k_window: int = 14, d_window: int = 3) -> dict:
        """Calculate Stochastic Oscillator"""
        high_max = data['High'].rolling(window=k_window).max()
        low_min = data['Low'].rolling(window=k_window).min()

        percent_k = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        percent_d = percent_k.rolling(window=d_window).mean()

        return {
            'K': percent_k,
            'D': percent_d
        }

    def calculate_macd(self, data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9, column: str = 'Close') -> dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = data[column].ewm(span=fast).mean()
        ema_slow = data[column].ewm(span=slow).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line

        return {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }

    def calculate_williams_r(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        high_max = data['High'].rolling(window=window).max()
        low_min = data['Low'].rolling(window=window).min()

        williams_r = -100 * ((high_max - data['Close']) / (high_max - low_min))

        return williams_r

    def calculate_cci(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        sma_tp = tp.rolling(window=window).mean()
        mad = tp.rolling(window=window).apply(lambda x: np.abs(x - x.mean()).mean())

        cci = (tp - sma_tp) / (0.015 * mad)

        return cci

    # Volatility Indicators
    def calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data['High']
        low = data['Low']
        close = data['Close']

        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.DataFrame([tr1, tr2, tr3]).max()
        atr = tr.rolling(window=window).mean()

        return atr

    def calculate_keltner_channels(self, data: pd.DataFrame, window: int = 20, multiplier: int = 2) -> dict:
        """Calculate Keltner Channels"""
        ema = self.calculate_ema(data, span=window)
        atr = self.calculate_atr(data, window)

        upper_channel = ema + (multiplier * atr)
        lower_channel = ema - (multiplier * atr)

        return {
            'Middle': ema,
            'Upper': upper_channel,
            'Lower': lower_channel
        }

    # Volume Indicators
    def calculate_obv(self, data: pd.DataFrame) -> pd.Series:
        """Calculate On-Balance Volume"""
        obv = np.where(data['Close'] > data['Close'].shift(), data['Volume'],
                      np.where(data['Close'] < data['Close'].shift(), -data['Volume'], 0)).cumsum()
        return pd.Series(obv, index=data.index)

    def calculate_volume_sma(self, data: pd.DataFrame, window: int = 20) -> pd.Series:
        """Calculate Volume Simple Moving Average"""
        return data['Volume'].rolling(window=window).mean()

    def calculate_volume_profile(self, data: pd.DataFrame, bins: int = 50) -> tuple:
        """Calculate Volume Profile"""
        price_range = np.linspace(data['Low'].min(), data['High'].max(), bins)
        volume_profile = []

        for i in range(len(price_range) - 1):
            mask = ((data['Close'] >= price_range[i]) &
                   (data['Close'] < price_range[i + 1]))
            volume_profile.append(data.loc[mask, 'Volume'].sum())

        return price_range[:-1], volume_profile

    # Support and Resistance Levels
    def calculate_pivot_points(self, data: pd.DataFrame) -> dict:
        """Calculate Pivot Points"""
        prev_high = data['High'].shift(1)
        prev_low = data['Low'].shift(1)
        prev_close = data['Close'].shift(1)

        pivot = (prev_high + prev_low + prev_close) / 3
        support1 = (2 * pivot) - prev_high
        support2 = pivot - (prev_high - prev_low)
        resistance1 = (2 * pivot) - prev_low
        resistance2 = pivot + (prev_high - prev_low)

        return {
            'Pivot': pivot,
            'Support1': support1,
            'Support2': support2,
            'Resistance1': resistance1,
            'Resistance2': resistance2
        }

    def calculate_fibonacci_retracements(self, data: pd.DataFrame, trend: str = 'up') -> dict:
        """Calculate Fibonacci Retracement Levels"""
        if trend == 'up':
            swing_low = data['Low'].min()
            swing_high = data['High'].max()
        else:
            swing_high = data['High'].max()
            swing_low = data['Low'].min()

        diff = swing_high - swing_low

        levels = {
            '0%': swing_high,
            '23.6%': swing_high - 0.236 * diff,
            '38.2%': swing_high - 0.382 * diff,
            '50%': swing_high - 0.5 * diff,
            '61.8%': swing_high - 0.618 * diff,
            '78.6%': swing_high - 0.786 * diff,
            '100%': swing_low
        }

        return levels

    def calculate_all_indicators(self, data: pd.DataFrame) -> dict:
        """Calculate all commonly used indicators"""
        indicators = {}

        # Trend indicators
        indicators['SMA_20'] = self.calculate_sma(data, 20)
        indicators['SMA_50'] = self.calculate_sma(data, 50)
        indicators['SMA_200'] = self.calculate_sma(data, 200)
        indicators['EMA_12'] = self.calculate_ema(data, 12)
        indicators['EMA_26'] = self.calculate_ema(data, 26)

        bollinger = self.calculate_bollinger_bands(data)
        indicators['BB_Upper'] = bollinger['Upper']
        indicators['BB_Middle'] = bollinger['Middle']
        indicators['BB_Lower'] = bollinger['Lower']

        # Momentum indicators
        indicators['RSI'] = self.calculate_rsi(data)
        indicators['Williams_R'] = self.calculate_williams_r(data)
        indicators['CCI'] = self.calculate_cci(data)

        macd = self.calculate_macd(data)
        indicators['MACD'] = macd['MACD']
        indicators['MACD_Signal'] = macd['Signal']
        indicators['MACD_Histogram'] = macd['Histogram']

        stochastic = self.calculate_stochastic(data)
        indicators['Stoch_K'] = stochastic['K']
        indicators['Stoch_D'] = stochastic['D']

        # Volatility indicators
        indicators['ATR'] = self.calculate_atr(data)

        keltner = self.calculate_keltner_channels(data)
        indicators['Keltner_Upper'] = keltner['Upper']
        indicators['Keltner_Lower'] = keltner['Lower']

        # Volume indicators
        indicators['OBV'] = self.calculate_obv(data)
        indicators['Volume_SMA'] = self.calculate_volume_sma(data)

        return indicators


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

    if args.all:
        indicators = tech_indicators.calculate_all_indicators(data)
        print(f"Calculated {len(indicators)} indicators for {args.ticker}")
    elif args.indicators:
        indicator_list = [i.strip() for i in args.indicators.split(',')]
        indicators = {}

        for ind in indicator_list:
            if hasattr(tech_indicators, f'calculate_{ind.lower()}'):
                try:
                    result = getattr(tech_indicators, f'calculate_{ind.lower()}')(data)
                    indicators[ind] = result
                    print(f"Calculated {ind}")
                except Exception as e:
                    print(f"Error calculating {ind}: {e}")
            else:
                print(f"Indicator {ind} not found")
    else:
        print("Please specify either --all or --indicators")
        return

    # Combine data with indicators
    if indicators:
        result_df = data.copy()
        for name, values in indicators.items():
            if isinstance(values, dict):
                for sub_name, sub_values in values.items():
                    result_df[f"{name}_{sub_name}"] = sub_values
            else:
                result_df[name] = values

        # Save or display results
        if args.output:
            result_df.to_csv(args.output)
            print(f"Results saved to {args.output}")
        else:
            print(f"\nRecent indicator values for {args.ticker}:")
            print(result_df.tail(10).round(2))


if __name__ == "__main__":
    main()
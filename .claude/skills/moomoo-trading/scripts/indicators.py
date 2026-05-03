"""
indicators.py — Technical Indicators for Moomoo Trading Skill

Delegates to the quantitative-trading skill's indicators module when available,
falling back to a standalone implementation. All function signatures are
identical to quantitative-trading, so scripts can use either interchangeably.

All functions accept an OHLCV DataFrame (columns: Open, High, Low, Close, Volume)
and return a pd.DataFrame with the indicator column(s).
"""

import os
import sys
import pandas as pd
import numpy as np


def _load_qt_indicators():
    """Try to import from quantitative-trading skill (same repo)."""
    skill_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..'))
    qt_path = os.path.join(skill_root, '.claude/skills/quantitative-trading')
    if os.path.isdir(qt_path) and qt_path not in sys.path:
        sys.path.insert(0, qt_path)
    try:
        from scripts.indicators import TechnicalIndicators
        return TechnicalIndicators()
    except ImportError:
        return None


_qt = _load_qt_indicators()


# ── Standalone fallback implementations ──────────────────────────────────────

def _rsi(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    close = data['Close']
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(window).mean()
    loss = (-delta.clip(upper=0)).rolling(window).mean()
    rs = gain / loss.replace(0, np.nan)
    return pd.DataFrame({'RSI': 100 - (100 / (1 + rs))}, index=data.index)


def _sma(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    return pd.DataFrame({'SMA': data['Close'].rolling(window).mean()}, index=data.index)


def _ema(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    return pd.DataFrame({'EMA': data['Close'].ewm(span=window, adjust=False).mean()}, index=data.index)


def _macd(data: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    close = data['Close']
    fast_ema = close.ewm(span=fast, adjust=False).mean()
    slow_ema = close.ewm(span=slow, adjust=False).mean()
    macd_line = fast_ema - slow_ema
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame({'MACD': macd_line, 'Signal': signal_line, 'Histogram': histogram}, index=data.index)


def _bollinger_bands(data: pd.DataFrame, window=20, num_std=2) -> pd.DataFrame:
    close = data['Close']
    mid = close.rolling(window).mean()
    std = close.rolling(window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    pct_b = (close - lower) / (upper - lower).replace(0, np.nan)
    return pd.DataFrame({'Upper': upper, 'Middle': mid, 'Lower': lower, '%B': pct_b}, index=data.index)


def _atr(data: pd.DataFrame, window=14) -> pd.DataFrame:
    high, low, close = data['High'], data['Low'], data['Close']
    prev_close = close.shift(1)
    tr = pd.concat([high - low, (high - prev_close).abs(), (low - prev_close).abs()], axis=1).max(axis=1)
    return pd.DataFrame({'ATR': tr.rolling(window).mean()}, index=data.index)


def _stochastic(data: pd.DataFrame, k_window=14, d_window=3) -> pd.DataFrame:
    low_min = data['Low'].rolling(k_window).min()
    high_max = data['High'].rolling(k_window).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min).replace(0, np.nan)
    d = k.rolling(d_window).mean()
    return pd.DataFrame({'K': k, 'D': d}, index=data.index)


# ── Public API (delegates to quantitative-trading if available) ───────────────

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    """Relative Strength Index. Returns DataFrame['RSI']."""
    if _qt:
        return _qt.calculate_rsi(data, window=window)
    return _rsi(data, window)


def calculate_sma(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Simple Moving Average. Returns DataFrame['SMA']."""
    if _qt:
        return _qt.calculate_sma(data, window)
    return _sma(data, window)


def calculate_ema(data: pd.DataFrame, window: int = 20) -> pd.DataFrame:
    """Exponential Moving Average. Returns DataFrame['EMA']."""
    if _qt:
        return _qt.calculate_ema(data, window=window)
    return _ema(data, window)


def calculate_macd(data: pd.DataFrame, fast=12, slow=26, signal=9) -> pd.DataFrame:
    """MACD. Returns DataFrame['MACD', 'Signal', 'Histogram']."""
    if _qt:
        return _qt.calculate_macd(data, fast, slow, signal)
    return _macd(data, fast, slow, signal)


def calculate_bollinger_bands(data: pd.DataFrame, window=20, num_std=2) -> pd.DataFrame:
    """Bollinger Bands. Returns DataFrame['Upper', 'Middle', 'Lower', '%B']."""
    if _qt:
        return _qt.calculate_bollinger_bands(data, window, num_std)
    return _bollinger_bands(data, window, num_std)


def calculate_atr(data: pd.DataFrame, window=14) -> pd.DataFrame:
    """Average True Range. Returns DataFrame['ATR']."""
    if _qt:
        return _qt.calculate_atr(data, window=window)
    return _atr(data, window)


def calculate_stochastic(data: pd.DataFrame, k_window=14, d_window=3) -> pd.DataFrame:
    """Stochastic Oscillator. Returns DataFrame['K', 'D']."""
    if _qt:
        return _qt.calculate_stochastic(data, k_window, d_window)
    return _stochastic(data, k_window, d_window)


def calculate_all(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all indicators and merge into one DataFrame.
    Useful for quick technical snapshots.

    Returns:
        DataFrame with all indicator columns appended to OHLCV data.
    """
    result = data.copy()
    for indicator_df in [
        calculate_rsi(data),
        calculate_macd(data),
        calculate_bollinger_bands(data),
        calculate_sma(data, 20),
        calculate_sma(data, 60),
        calculate_ema(data, 20),
        calculate_atr(data),
        calculate_stochastic(data),
    ]:
        for col in indicator_df.columns:
            result[col] = indicator_df[col]
    return result

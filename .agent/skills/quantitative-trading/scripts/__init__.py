"""
Quantitative Trading Scripts
Core implementation modules for quantitative analysis.

This package provides unified exports for all core functionality.
"""

# Import core classes
from .data_fetcher import DataFetcher
from .indicators import TechnicalIndicators
from .strategies import TradingStrategy
from .backtester import Backtester
from .portfolio_optimization import PortfolioAnalyzer
from .risk_manager import RiskManager

# Aliases for backward compatibility
TradingStrategies = TradingStrategy

# Create default instances for convenience functions
_data_fetcher = DataFetcher()
_indicators = TechnicalIndicators()
_strategies = TradingStrategy()
_backtester = Backtester()
_portfolio_analyzer = PortfolioAnalyzer()
_risk_manager = RiskManager()


# ============================================================
# Convenience Functions - Data Fetching
# ============================================================

def fetch_stock_data(ticker, start_date=None, end_date=None, period='1y', 
                     provider=None, market=None):
    """
    Fetch stock data for a ticker.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPL', '000001.SZ')
        start_date: Start date 'YYYY-MM-DD'
        end_date: End date 'YYYY-MM-DD'
        period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max'
        provider: 'yfinance', 'tushare', or None (auto)
        market: Market hint ('cn', 'hk', 'us')
    
    Returns:
        pd.DataFrame with OHLCV and calculated fields
    """
    return _data_fetcher.fetch_stock_data(ticker, start_date, end_date, period, 
                                          provider=provider, market=market)


def fetch_multiple_stocks(tickers, start_date=None, end_date=None, period='1y',
                         provider=None, market=None):
    """Fetch data for multiple stocks."""
    return _data_fetcher.fetch_multiple_stocks(tickers, start_date, end_date, period,
                                               provider=provider, market=market)


def get_company_info(ticker, provider=None, market=None):
    """Get company fundamentals."""
    return _data_fetcher.get_company_info(ticker, provider=provider, market=market)


def calculate_correlation_matrix(tickers, period='1y', provider=None, market=None):
    """Calculate return correlation between stocks."""
    return _data_fetcher.calculate_correlation_matrix(tickers, period, 
                                                      provider=provider, market=market)


# ============================================================
# Convenience Functions - Indicators
# ============================================================

def calculate_sma(data, window=20):
    """Simple Moving Average."""
    return _indicators.calculate_sma(data, window)



def calculate_ema(data, window=20):
    """Exponential Moving Average."""
    return _indicators.calculate_ema(data, window=window)


def calculate_rsi(data, window=14):
    """Relative Strength Index.
    
    Note: Uses 'window' parameter to match underlying RSI calculation.
    """
    return _indicators.calculate_rsi(data, window=window)


def calculate_macd(data, fast=12, slow=26, signal=9):
    """MACD indicator."""
    return _indicators.calculate_macd(data, fast, slow, signal)


def calculate_bollinger_bands(data, window=20, num_std=2):
    """Bollinger Bands."""
    return _indicators.calculate_bollinger_bands(data, window, num_std)


def calculate_atr(data, window=14):
    """Average True Range."""
    return _indicators.calculate_atr(data, window=window)


def calculate_adx(data, window=14):
    """Average Directional Index."""
    return _indicators.calculate_adx(data, window=window)


def calculate_stochastic(data, k_window=14, d_window=3):
    """Stochastic Oscillator."""
    return _indicators.calculate_stochastic(data, k_window, d_window)


def calculate_williams_r(data, window=14):
    """Williams %R."""
    return _indicators.calculate_williams_r(data, window=window)


def calculate_cci(data, window=20):
    """Commodity Channel Index."""
    return _indicators.calculate_cci(data, window=window)


def calculate_obv(data):
    """On-Balance Volume."""
    return _indicators.calculate_obv(data)


# ============================================================
# Convenience Functions - Strategies
# ============================================================

def moving_average_crossover(data, fast_window=20, slow_window=50):
    """Generate MA crossover signals."""
    return _strategies.moving_average_crossover(data, fast_window, slow_window)


def rsi_mean_reversion(data, oversold=30, overbought=70):
    """Generate RSI mean reversion signals."""
    return _strategies.rsi_mean_reversion(data, oversold, overbought)


# ============================================================
# Convenience Functions - Risk
# ============================================================

def calculate_var(returns, confidence_level=0.95):
    """Value at Risk."""
    return _risk_manager.calculate_var(returns, method='historical', confidence_level=confidence_level)


def calculate_cvar(returns, confidence_level=0.95):
    """Conditional Value at Risk (Expected Shortfall)."""
    return _risk_manager.calculate_cvar(returns, confidence_level=confidence_level)


def calculate_max_drawdown(data):
    """Maximum drawdown."""
    metrics = _risk_manager.calculate_drawdown_metrics(data, is_returns=False)
    return metrics['max_drawdown']


def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
    """Calculate Sharpe Ratio."""
    metrics = _risk_manager.calculate_risk_adjusted_metrics(returns, risk_free_rate=risk_free_rate)
    return metrics['sharpe_ratio']


def calculate_sortino_ratio(returns, risk_free_rate=0.02):
    """Calculate Sortino Ratio."""
    metrics = _risk_manager.calculate_risk_adjusted_metrics(returns, risk_free_rate=risk_free_rate)
    return metrics['sortino_ratio']


# ============================================================
# Exports
# ============================================================

__all__ = [
    # Classes
    'DataFetcher',
    'TechnicalIndicators',
    'TradingStrategies',
    'Backtester',
    'PortfolioAnalyzer',
    'RiskManager',
    # Data functions
    'fetch_stock_data',
    'fetch_multiple_stocks',
    'get_company_info',
    'calculate_correlation_matrix',
    # Indicator functions
    'calculate_sma',
    'calculate_ema',
    'calculate_rsi',
    'calculate_macd',
    'calculate_bollinger_bands',
    'calculate_atr',
    'calculate_adx',
    'calculate_stochastic',
    'calculate_williams_r',
    'calculate_cci',
    'calculate_obv',
    # Strategy functions
    'moving_average_crossover',
    'rsi_mean_reversion',
    # Risk functions
    'calculate_var',
    'calculate_cvar',
    'calculate_max_drawdown',
    'calculate_sharpe_ratio',
    'calculate_sortino_ratio',
]

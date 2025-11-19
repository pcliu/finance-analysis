"""
Data Fetcher API
Fetch stock data, company information, and market indices.
"""

from .fetch_stock_data import fetch_stock_data, fetch_stock_data_async
from .fetch_multiple_stocks import fetch_multiple_stocks, fetch_multiple_stocks_async
from .get_company_info import get_company_info, get_company_info_async
from .fetch_market_indices import fetch_market_indices, fetch_market_indices_async
from .calculate_correlation_matrix import calculate_correlation_matrix, calculate_correlation_matrix_async
from .get_data_summary import get_data_summary, get_data_summary_async

__all__ = [
    'fetch_stock_data',
    'fetch_multiple_stocks',
    'get_company_info',
    'fetch_market_indices',
    'calculate_correlation_matrix',
    'get_data_summary',
    'fetch_stock_data_async',
    'fetch_multiple_stocks_async',
    'get_company_info_async',
    'fetch_market_indices_async',
    'calculate_correlation_matrix_async',
    'get_data_summary_async',
]

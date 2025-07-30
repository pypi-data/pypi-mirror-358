"""
TinyShare - A lightweight wrapper for tushare financial data API

This package provides a drop-in replacement for tushare with additional
features and optimizations while maintaining 100% API compatibility.
"""

import tushare as _tushare
import functools
import logging
from typing import Any, Optional

__version__ = "0.1.0"
__author__ = "Your Name"

# Set up logging
logger = logging.getLogger(__name__)

# Global token storage
_token = None


def set_token(token: str) -> None:
    """
    Set the tushare API token.
    
    Args:
        token (str): Your tushare API token
    """
    global _token
    _token = token
    _tushare.set_token(token)
    logger.info("Token set successfully")


def get_token() -> Optional[str]:
    """
    Get the current tushare API token.
    
    Returns:
        str or None: Current token if set, None otherwise
    """
    return _token


def pro_api(token: Optional[str] = None, timeout: int = 30) -> Any:
    """
    Initialize tushare pro API client.
    
    Args:
        token (str, optional): API token. If not provided, uses globally set token.
        timeout (int): Request timeout in seconds. Defaults to 30.
    
    Returns:
        TuShare Pro API client instance
    """
    if token:
        set_token(token)
    elif not _token:
        raise ValueError("Token not set. Please call set_token() first or provide token parameter.")
    
    try:
        client = _tushare.pro_api(token=token, timeout=timeout)
        logger.info("Pro API client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize pro API client: {e}")
        raise


# Proxy all other tushare functions and attributes
def __getattr__(name: str) -> Any:
    """
    Proxy all tushare attributes and functions.
    
    This allows tinyshare to act as a complete drop-in replacement for tushare
    while maintaining the ability to add custom functionality.
    """
    if hasattr(_tushare, name):
        attr = getattr(_tushare, name)
        
        # If it's a callable, wrap it with logging
        if callable(attr):
            @functools.wraps(attr)
            def wrapper(*args, **kwargs):
                logger.debug(f"Calling tushare.{name} with args={args}, kwargs={kwargs}")
                try:
                    result = attr(*args, **kwargs)
                    logger.debug(f"tushare.{name} completed successfully")
                    return result
                except Exception as e:
                    logger.error(f"Error in tushare.{name}: {e}")
                    raise
            return wrapper
        else:
            return attr
    else:
        raise AttributeError(f"module 'tinyshare' has no attribute '{name}'")


# Export commonly used functions directly
from tushare import get_hist_data, get_tick_data, get_today_all, get_realtime_quotes

# Make sure we export the main functions
__all__ = [
    'set_token',
    'get_token', 
    'pro_api',
    'get_hist_data',
    'get_tick_data',
    'get_today_all',
    'get_realtime_quotes',
    '__version__'
] 
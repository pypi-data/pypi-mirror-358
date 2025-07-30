"""
StockFetch - Think Neofetch for stocks
"""

from .Pyfinance import ticker, make_ascii, validate_ticker

__version__ = "1.0.0"
__all__ = ["ticker", "make_ascii", "validate_ticker"]

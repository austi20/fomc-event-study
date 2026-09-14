"""Download and cache daily prices, convert to log returns."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"

TICKERS = ["SPY", "KRE", "XLF", "TLT"]
START = "2014-01-01"


def fetch_prices(tickers: list[str] = TICKERS, start: str = START) -> pd.DataFrame:
    """Adjusted closes from yfinance, cached to data/raw/ on first fetch."""
    raise NotImplementedError


def to_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    raise NotImplementedError

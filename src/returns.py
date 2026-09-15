"""Download and cache daily prices, convert to log returns."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
PRICES_CACHE = RAW_DIR / "prices.parquet"

TICKERS = ["SPY", "KRE", "XLF", "TLT"]
START = "2014-01-01"


def fetch_prices(tickers: list[str] = TICKERS, start: str = START) -> pd.DataFrame:
    """Adjusted closes from yfinance, cached to data/raw/ on first fetch."""
    if PRICES_CACHE.exists():
        return pd.read_parquet(PRICES_CACHE)

    import yfinance as yf  # lazy: only needed on a cache miss

    prices = yf.download(tickers, start=start, auto_adjust=True, progress=False)["Close"]
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    prices.to_parquet(PRICES_CACHE)
    return prices


def to_log_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Daily log returns; drops the first row (no prior price)."""
    return np.log(prices / prices.shift(1)).iloc[1:]

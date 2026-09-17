"""Tests for price fetching/caching and log-return conversion."""

import numpy as np
import pandas as pd
import pytest

from src import returns as returns_mod


@pytest.fixture
def cache_dir(tmp_path, monkeypatch):
    path = tmp_path / "data" / "raw"
    monkeypatch.setattr(returns_mod, "RAW_DIR", path)
    monkeypatch.setattr(returns_mod, "PRICES_CACHE", path / "prices.parquet")
    return path


def test_cache_hit_never_calls_yfinance(cache_dir, monkeypatch):
    cache_dir.mkdir(parents=True)
    expected = pd.DataFrame({"SPY": [100.0, 101.0]})
    expected.to_parquet(returns_mod.PRICES_CACHE)

    def boom(*args, **kwargs):
        raise AssertionError("cache hit must not call yfinance")

    monkeypatch.setattr(returns_mod.yf, "download", boom)
    pd.testing.assert_frame_equal(returns_mod.fetch_prices(), expected)


def test_cache_miss_downloads_and_writes_cache(cache_dir, monkeypatch):
    cols = pd.MultiIndex.from_tuples([("Close", "SPY"), ("Close", "KRE")], names=["Price", "Ticker"])
    raw = pd.DataFrame([[100.0, 50.0], [102.0, 49.0]], columns=cols)
    monkeypatch.setattr(returns_mod.yf, "download", lambda *args, **kwargs: raw)

    result = returns_mod.fetch_prices(["SPY", "KRE"])
    assert list(result.columns) == ["SPY", "KRE"]
    assert returns_mod.PRICES_CACHE.exists()
    pd.testing.assert_frame_equal(pd.read_parquet(returns_mod.PRICES_CACHE), result)


def test_log_returns_matches_known_values():
    prices = pd.DataFrame({"SPY": [100.0, 110.0, 99.0]})
    result = returns_mod.to_log_returns(prices)
    expected = pd.DataFrame({"SPY": [np.log(1.1), np.log(0.9)]}, index=[1, 2])
    pd.testing.assert_frame_equal(result, expected)


def test_log_returns_drops_first_row():
    prices = pd.DataFrame({"SPY": [100.0, 101.0]})
    assert len(returns_mod.to_log_returns(prices)) == 1

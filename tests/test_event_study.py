"""Tests for the event-study math. Keep these cheap and deterministic."""

import numpy as np
import pandas as pd
import pytest

from src.event_study import (
    ESTIMATION_WINDOW,
    EVENT_WINDOW,
    MARKET_TICKER,
    aar_by_offset,
    abnormal_returns,
    cumulative_abnormal_returns,
    estimate_market_model,
)


def test_market_model_recovers_known_alpha_beta():
    rng = np.random.default_rng(0)
    market = pd.Series(rng.normal(0, 0.01, 300))
    alpha0, beta0 = 0.0005, 1.3
    returns = alpha0 + beta0 * market
    alpha, beta = estimate_market_model(returns, market)
    assert alpha == pytest.approx(alpha0)
    assert beta == pytest.approx(beta0)


def _synthetic_returns(n_days=400):
    """SPY and KRE returns with a known, noise-free market-model relationship."""
    rng = np.random.default_rng(1)
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    spy = rng.normal(0, 0.01, n_days)
    kre = 0.0002 + 1.5 * spy
    return pd.DataFrame({"SPY": spy, "KRE": kre}, index=dates)


def test_abnormal_return_is_zero_when_regression_model_is_exact():
    # KRE is an exact linear function of SPY, so its market-model AR is ~0.
    # SPY itself uses a constant-mean model, so its own AR need not be zero.
    returns = _synthetic_returns()
    events = pd.DataFrame({"date": [returns.index[300]]})
    ar = abnormal_returns(returns, events)
    kre_ar = ar[ar["ticker"] == "KRE"]["abnormal_return"]
    assert np.allclose(kre_ar, 0, atol=1e-10)


def test_spy_uses_constant_mean_not_regression_on_itself():
    returns = _synthetic_returns()
    event_idx = 300
    events = pd.DataFrame({"date": [returns.index[event_idx]]})
    ar = abnormal_returns(returns, events)
    spy_rows = ar[ar["ticker"] == MARKET_TICKER]

    est_window = returns["SPY"].iloc[
        event_idx + ESTIMATION_WINDOW[0] : event_idx + ESTIMATION_WINDOW[1] + 1
    ]
    expected_alpha = est_window.mean()
    for _, row in spy_rows.iterrows():
        actual_return = returns.loc[row["date"], "SPY"]
        assert row["abnormal_return"] == pytest.approx(actual_return - expected_alpha, abs=1e-12)


def test_one_row_per_ticker_event_offset():
    returns = _synthetic_returns()
    events = pd.DataFrame({"date": [returns.index[300]]})
    ar = abnormal_returns(returns, events)
    n_offsets = EVENT_WINDOW[1] - EVENT_WINDOW[0] + 1
    assert len(ar) == len(returns.columns) * n_offsets
    assert set(ar["offset"]) == set(range(EVENT_WINDOW[0], EVENT_WINDOW[1] + 1))


def test_event_on_closed_day_rolls_forward_to_next_trading_day():
    returns = _synthetic_returns()
    monday = next(d for d in returns.index[250:] if d.dayofweek == 0)
    sunday_before = monday - pd.Timedelta(days=1)
    assert sunday_before not in returns.index
    trading_day = monday

    ar_from_sunday = abnormal_returns(returns, pd.DataFrame({"date": [sunday_before]}))
    ar_from_trading_day = abnormal_returns(returns, pd.DataFrame({"date": [trading_day]}))
    pd.testing.assert_frame_equal(
        ar_from_sunday.drop(columns="event_date"),
        ar_from_trading_day.drop(columns="event_date"),
    )


def test_event_without_enough_estimation_history_is_skipped():
    returns = _synthetic_returns()
    early_event = returns.index[10]  # fewer than 250 prior trading days
    events = pd.DataFrame({"date": [early_event]})
    ar = abnormal_returns(returns, events)
    assert ar.empty


def test_cumulative_abnormal_returns_sums_event_window():
    ar = pd.DataFrame(
        {
            "ticker": ["SPY", "SPY", "SPY", "KRE", "KRE", "KRE"],
            "event_date": pd.to_datetime(["2020-01-01"] * 6),
            "offset": [-1, 0, 1, -1, 0, 1],
            "abnormal_return": [0.01, 0.02, -0.01, 0.05, 0.05, 0.05],
        }
    )
    car = cumulative_abnormal_returns(ar).set_index("ticker")["car"]
    assert car["SPY"] == pytest.approx(0.02)
    assert car["KRE"] == pytest.approx(0.15)


def test_aar_by_offset_averages_across_events():
    ar = pd.DataFrame(
        {
            "ticker": ["KRE", "KRE"],
            "event_date": pd.to_datetime(["2020-01-01", "2020-02-01"]),
            "offset": [0, 0],
            "abnormal_return": [0.02, 0.06],
        }
    )
    aar = aar_by_offset(ar).set_index(["ticker", "offset"])["aar"]
    assert aar[("KRE", 0)] == pytest.approx(0.04)

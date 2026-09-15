"""Market-model estimation, abnormal returns, and CAR aggregation.

Estimation window: [t-250, t-30]. Event window: [-1, +1].
For SPY itself use a constant-mean model -- do not regress a series on itself.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.fomc_dates import EVENTS_CSV
from src.returns import fetch_prices, to_log_returns

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
AR_PARQUET = DATA_DIR / "abnormal_returns.parquet"
AAR_CSV = DATA_DIR / "aar_by_offset.csv"

ESTIMATION_WINDOW = (-250, -30)
EVENT_WINDOW = (-1, 1)
MARKET_TICKER = "SPY"


def estimate_market_model(returns: pd.Series, market: pd.Series) -> tuple[float, float]:
    """Return (alpha, beta) fit over the estimation window."""
    beta, alpha = np.polyfit(market, returns, 1)
    return alpha, beta


def abnormal_returns(returns: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Tidy frame: one row per (ticker, event_date, offset) with AR.

    Skips events with less than a full estimation window of history.
    """
    dates = returns.index
    rows = []
    for event_date in pd.to_datetime(events["date"]):
        # roll forward if not a trading day (e.g. 2020-03-15 was a Sunday)
        event_idx = dates.searchsorted(event_date)
        if event_idx >= len(dates):
            continue
        est_start = event_idx + ESTIMATION_WINDOW[0]
        est_end = event_idx + ESTIMATION_WINDOW[1]
        if est_start < 0:
            continue
        window = returns.iloc[est_start : est_end + 1]

        for ticker in returns.columns:
            if ticker == MARKET_TICKER:
                alpha, beta = window[ticker].mean(), 0.0
            else:
                alpha, beta = estimate_market_model(window[ticker], window[MARKET_TICKER])

            for offset in range(EVENT_WINDOW[0], EVENT_WINDOW[1] + 1):
                event_pos = event_idx + offset
                if not 0 <= event_pos < len(dates):
                    continue
                r = returns[ticker].iloc[event_pos]
                r_market = returns[MARKET_TICKER].iloc[event_pos]
                rows.append(
                    {
                        "ticker": ticker,
                        "event_date": event_date,
                        "offset": offset,
                        "date": dates[event_pos],
                        "return": r,
                        "abnormal_return": r - (alpha + beta * r_market),
                    }
                )
    return pd.DataFrame(rows)


def cumulative_abnormal_returns(ar: pd.DataFrame) -> pd.DataFrame:
    """CAR per (ticker, event_date) across the event window."""
    return ar.groupby(["ticker", "event_date"])["abnormal_return"].sum().reset_index(name="car")


def aar_by_offset(ar: pd.DataFrame) -> pd.DataFrame:
    """Average abnormal return per (ticker, offset) across all events."""
    return ar.groupby(["ticker", "offset"])["abnormal_return"].mean().reset_index(name="aar")


if __name__ == "__main__":
    events = pd.read_csv(EVENTS_CSV)
    returns = to_log_returns(fetch_prices())

    ar = abnormal_returns(returns, events)
    ar.to_parquet(AR_PARQUET, index=False)

    aar_by_offset(ar).to_csv(AAR_CSV, index=False)

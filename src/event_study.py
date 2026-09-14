"""Market-model estimation, abnormal returns, and CAR aggregation.

Estimation window: [t-250, t-30]. Event window: [-1, +1].
For SPY itself use a constant-mean model -- do not regress a series on itself.
"""

from __future__ import annotations

import pandas as pd

ESTIMATION_WINDOW = (-250, -30)
EVENT_WINDOW = (-1, 1)


def estimate_market_model(returns: pd.Series, market: pd.Series) -> tuple[float, float]:
    """Return (alpha, beta) fit over the estimation window."""
    raise NotImplementedError


def abnormal_returns(returns: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Tidy frame: one row per (ticker, event_date, offset) with AR."""
    raise NotImplementedError


def cumulative_abnormal_returns(ar: pd.DataFrame) -> pd.DataFrame:
    """CAR per (ticker, event_date) across the event window."""
    raise NotImplementedError

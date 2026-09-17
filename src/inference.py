"""Hypothesis tests and bootstrap confidence intervals.

Bootstrap is seeded so results are reproducible.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20260918
N_BOOT = 10_000


def ttest_aar(ar: pd.DataFrame) -> pd.DataFrame:
    """One-sample t-test of AAR != 0 at each (ticker, offset)."""
    rows = []
    for (ticker, offset), group in ar.groupby(["ticker", "offset"]):
        values = group["abnormal_return"].to_numpy()
        t_stat, p_value = stats.ttest_1samp(values, 0.0)
        rows.append(
            {
                "ticker": ticker,
                "offset": offset,
                "aar": values.mean(),
                "t_stat": t_stat,
                "p_value": p_value,
                "n": len(values),
            }
        )
    return pd.DataFrame(rows)


def bootstrap_ci(values: np.ndarray, n_boot: int = N_BOOT, seed: int = SEED) -> tuple[float, float]:
    """95% percentile bootstrap CI for the mean."""
    values = np.asarray(values)
    rng = np.random.default_rng(seed)

    means = []
    for _ in range(n_boot):
        sample = rng.choice(values, size=len(values), replace=True)
        means.append(sample.mean())

    lo, hi = np.percentile(means, [2.5, 97.5])
    return float(lo), float(hi)


def diff_in_means_ci(
    a: np.ndarray, b: np.ndarray, n_boot: int = N_BOOT, seed: int = SEED
) -> tuple[float, float]:
    """Bootstrap CI for mean(a) - mean(b), paired by event (e.g. KRE CAR vs SPY CAR).

    Each resample redraws events rather than tickers, so a ticker's CAR stays
    matched to the market's CAR on the same FOMC date.
    """
    a, b = np.asarray(a), np.asarray(b)
    if len(a) != len(b):
        raise ValueError("a and b must be paired by event (same length)")
    rng = np.random.default_rng(seed)

    diffs = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(a), size=len(a))
        diffs.append(a[idx].mean() - b[idx].mean())

    lo, hi = np.percentile(diffs, [2.5, 97.5])
    return float(lo), float(hi)

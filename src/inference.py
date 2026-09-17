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
    idx = rng.integers(0, len(values), size=(n_boot, len(values)))
    boot_means = values[idx].mean(axis=1)
    lo, hi = np.percentile(boot_means, [2.5, 97.5])
    return float(lo), float(hi)


def diff_in_means_ci(
    a: np.ndarray, b: np.ndarray, n_boot: int = N_BOOT, seed: int = SEED
) -> tuple[float, float]:
    """Bootstrap CI for mean(a) - mean(b), paired by event (e.g. KRE CAR vs SPY CAR).

    a and b must be the same length and aligned to the same events, since each
    resample redraws events (not tickers) to preserve the correlation between
    a ticker's CAR and the market-wide CAR on the same FOMC date.
    """
    a, b = np.asarray(a), np.asarray(b)
    if len(a) != len(b):
        raise ValueError("a and b must be paired by event (same length)")
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, len(a), size=(n_boot, len(a)))
    diff = a[idx].mean(axis=1) - b[idx].mean(axis=1)
    lo, hi = np.percentile(diff, [2.5, 97.5])
    return float(lo), float(hi)

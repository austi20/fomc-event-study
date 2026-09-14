"""Hypothesis tests and bootstrap confidence intervals.

Bootstrap is seeded so results are reproducible.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20260918
N_BOOT = 10_000


def ttest_aar(ar: pd.DataFrame) -> pd.DataFrame:
    """One-sample t-test of AAR != 0 at each event-day offset."""
    raise NotImplementedError


def bootstrap_ci(values: np.ndarray, n_boot: int = N_BOOT, seed: int = SEED) -> tuple[float, float]:
    """95% percentile bootstrap CI for the mean."""
    raise NotImplementedError


def diff_in_means_ci(a: np.ndarray, b: np.ndarray, n_boot: int = N_BOOT, seed: int = SEED):
    """Bootstrap CI for mean(a) - mean(b), e.g. KRE CAR vs SPY CAR."""
    raise NotImplementedError

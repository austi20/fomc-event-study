"""Tests for hypothesis tests and bootstrap CIs. Keep these cheap and deterministic."""

import numpy as np
import pandas as pd
import pytest

from src.inference import bootstrap_ci, diff_in_means_ci, release_day_summary, ttest_aar


def test_ttest_aar_one_row_per_ticker_offset():
    ar = pd.DataFrame(
        {
            "ticker": ["SPY", "SPY", "SPY", "SPY", "KRE", "KRE", "KRE", "KRE"],
            "offset": [0, 0, 1, 1, 0, 0, 1, 1],
            "abnormal_return": [0.01, 0.012, 0.02, 0.018, 0.03, 0.028, 0.04, 0.038],
        }
    )
    result = ttest_aar(ar)
    assert len(result) == 4
    assert set(zip(result["ticker"], result["offset"])) == {
        ("SPY", 0),
        ("SPY", 1),
        ("KRE", 0),
        ("KRE", 1),
    }


def test_ttest_aar_rejects_when_mean_is_far_from_zero():
    rng = np.random.default_rng(0)
    ar = pd.DataFrame(
        {
            "ticker": ["KRE"] * 200,
            "offset": [0] * 200,
            "abnormal_return": rng.normal(0.01, 0.001, 200),
        }
    )
    result = ttest_aar(ar)
    assert result.loc[0, "p_value"] < 0.001


def test_ttest_aar_fails_to_reject_pure_noise():
    rng = np.random.default_rng(0)
    ar = pd.DataFrame(
        {
            "ticker": ["KRE"] * 200,
            "offset": [0] * 200,
            "abnormal_return": rng.normal(0.0, 0.01, 200),
        }
    )
    result = ttest_aar(ar)
    assert result.loc[0, "p_value"] > 0.05


def test_bootstrap_ci_seeded_is_reproducible():
    values = np.array([0.01, -0.02, 0.03, 0.0, 0.015, -0.01])
    ci_a = bootstrap_ci(values, seed=42)
    ci_b = bootstrap_ci(values, seed=42)
    assert ci_a == ci_b


def test_bootstrap_ci_contains_the_sample_mean():
    rng = np.random.default_rng(1)
    values = rng.normal(0.005, 0.01, 500)
    lo, hi = bootstrap_ci(values)
    assert lo < values.mean() < hi


def test_bootstrap_ci_excludes_zero_for_a_strong_effect():
    rng = np.random.default_rng(2)
    values = rng.normal(0.05, 0.005, 300)
    lo, _ = bootstrap_ci(values)
    assert lo > 0


def test_diff_in_means_ci_requires_paired_equal_length():
    with pytest.raises(ValueError):
        diff_in_means_ci(np.array([0.1, 0.2]), np.array([0.1, 0.2, 0.3]))


def test_diff_in_means_ci_centered_on_observed_difference():
    rng = np.random.default_rng(3)
    a = rng.normal(0.02, 0.01, 200)
    b = rng.normal(0.005, 0.01, 200)
    lo, hi = diff_in_means_ci(a, b)
    assert lo < (a.mean() - b.mean()) < hi
    # a is drawn with a clearly larger mean than b, so the CI should exclude 0.
    assert lo > 0


def _day_rows():
    return pd.DataFrame(
        {
            "ticker": ["TLT", "TLT", "TLT", "TLT", "TLT", "TLT"],
            "decision": ["hike", "hike", "cut", "cut", "hike", "cut"],
            "offset": [0, 0, 0, 0, 1, 1],
            "return": [0.02, 0.04, -0.01, -0.03, 0.5, 0.5],
            "abnormal_return": [0.01, 0.03, -0.02, -0.04, 0.5, 0.5],
        }
    )


def test_release_day_summary_uses_only_offset_zero():
    result = release_day_summary(_day_rows(), ["ticker"])
    assert len(result) == 1
    assert result.loc[0, "n"] == 4
    assert result.loc[0, "mean"] == pytest.approx(-0.005)


def test_release_day_summary_splits_by_decision():
    result = release_day_summary(_day_rows(), ["decision", "ticker"]).set_index("decision")
    assert result.loc["hike", "mean"] == pytest.approx(0.02)
    assert result.loc["cut", "mean"] == pytest.approx(-0.03)
    assert result.loc["hike", "ci_lo"] <= 0.02 <= result.loc["hike", "ci_hi"]


def test_release_day_summary_can_use_raw_returns():
    result = release_day_summary(_day_rows(), ["decision", "ticker"], value_col="return")
    by_decision = result.set_index("decision")["mean"]
    assert by_decision["hike"] == pytest.approx(0.03)
    assert by_decision["cut"] == pytest.approx(-0.02)

"""Smoke test for the TLT benchmark figure."""

import pandas as pd

from src.plots import plot_tlt_benchmarks


def test_plot_tlt_benchmarks_writes_a_png(tmp_path):
    rows = []
    for series in ["TLT raw return", "TLT vs AGG"]:
        for group, n in [("All", 94), ("Hike", 20), ("Cut", 11), ("Hold", 63)]:
            rows.append(
                {"series": series, "group": group, "n": n, "mean": 0.003, "ci_lo": 0.001, "ci_hi": 0.005}
            )
    out = plot_tlt_benchmarks(pd.DataFrame(rows), out=tmp_path / "tlt.png")
    assert out.exists()
    assert out.stat().st_size > 0

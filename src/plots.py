"""Figures: AAR by offset with CI bands, and the CAR distribution."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.ticker import MaxNLocator

from src.inference import bootstrap_ci

FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"

# Fixed ticker -> color mapping, shared across figures (identity, not rank).
TICKER_COLORS = {
    "SPY": "#2a78d6",  # blue
    "KRE": "#eb6834",  # orange
    "XLF": "#1baf7a",  # aqua
    "TLT": "#eda100",  # yellow
}
INK = "#0b0b0b"
MUTED = "#898781"
GRID = "#e1e0d9"


def _style_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(MUTED)
    ax.spines["bottom"].set_color(MUTED)
    ax.tick_params(colors=MUTED)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)


def plot_aar_by_offset(ar: pd.DataFrame, out: Path = FIGURES_DIR / "aar_by_offset.png") -> Path:
    """AAR per ticker at each event-day offset, with a 95% bootstrap CI band."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    tickers = [t for t in TICKER_COLORS if t in ar["ticker"].unique()]

    for ticker in tickers:
        group = ar[ar["ticker"] == ticker]
        offsets = sorted(group["offset"].unique())
        means, los, his = [], [], []
        for offset in offsets:
            values = group.loc[group["offset"] == offset, "abnormal_return"].to_numpy()
            means.append(values.mean())
            lo, hi = bootstrap_ci(values)
            los.append(lo)
            his.append(hi)
        color = TICKER_COLORS[ticker]
        ax.plot(offsets, means, marker="o", markersize=6, linewidth=2, color=color, label=ticker, zorder=3)
        ax.fill_between(offsets, los, his, color=color, alpha=0.15, linewidth=0, zorder=2)

    ax.axhline(0, color=MUTED, linewidth=1, zorder=1)
    ax.set_xticks(sorted(ar["offset"].unique()))
    ax.set_xlabel("Event-day offset", color=INK)
    ax.set_ylabel("Average abnormal return", color=INK)
    ax.set_title("AAR around FOMC statement releases (95% bootstrap CI)", color=INK)
    _style_axes(ax)
    ax.legend(frameon=False, labelcolor=INK)
    fig.tight_layout()

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_car_distribution(car: pd.DataFrame, out: Path = FIGURES_DIR / "car_distribution.png") -> Path:
    """Distribution of per-event CAR for each ticker, with mean and 95% bootstrap CI marked."""
    tickers = [t for t in TICKER_COLORS if t in car["ticker"].unique()]
    fig, axes = plt.subplots(2, 2, figsize=(9, 6.5), sharex=True)

    for ax, ticker in zip(axes.flat, tickers):
        values = car.loc[car["ticker"] == ticker, "car"].to_numpy()
        color = TICKER_COLORS[ticker]
        ax.hist(values, bins=20, color=color, alpha=0.6, edgecolor="white", zorder=2)
        mean = values.mean()
        lo, hi = bootstrap_ci(values)
        ax.axvspan(lo, hi, color=color, alpha=0.15, linewidth=0, zorder=1)
        ax.axvline(mean, color=INK, linewidth=1.5, linestyle="--", zorder=3)
        ax.set_title(ticker, color=INK, loc="left", fontsize=11)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        _style_axes(ax)

    fig.supxlabel("Cumulative abnormal return, [-1, +1] window", color=INK)
    fig.suptitle("Distribution of per-event CAR (dashed = mean, shaded = 95% bootstrap CI)", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out

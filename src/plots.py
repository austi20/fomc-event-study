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
# shape differs too, so color is never the only cue
TLT_SERIES_STYLES = {
    "TLT raw return": (TICKER_COLORS["TLT"], "o"),
    "TLT vs AGG": ("#e87ba4", "D"),  # magenta, next palette slot
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
    """AAR per ticker at each event day offset, with a 95% bootstrap CI band."""
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
    ax.set_xlabel("Event day offset", color=INK)
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.1%}")
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
    """Distribution of per event CAR for each ticker, with mean and 95% bootstrap CI marked."""
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
        ax.xaxis.set_major_formatter(lambda x, _: f"{x:.0%}")
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        _style_axes(ax)

    fig.supxlabel("Cumulative abnormal return, [-1, +1] window", color=INK)
    fig.supylabel("Events", color=INK)
    fig.suptitle("Distribution of per event CAR (dashed = mean, shaded = 95% bootstrap CI)", color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.96))

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def plot_tlt_benchmarks(
    summary: pd.DataFrame,
    groups: tuple[str, ...] = ("All", "Hike", "Cut", "Hold"),
    out: Path = FIGURES_DIR / "tlt_by_decision.png",
) -> Path:
    """TLT release day mean and 95% bootstrap CI, raw and against AGG, per decision group."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    shift = 0.15

    for i, (series, (color, marker)) in enumerate(TLT_SERIES_STYLES.items()):
        rows = summary[summary["series"] == series].set_index("group").loc[list(groups)]
        side = -1 if i == 0 else 1
        xs = [g + side * shift for g in range(len(groups))]
        means = rows["mean"].to_numpy()
        errors = [means - rows["ci_lo"].to_numpy(), rows["ci_hi"].to_numpy() - means]
        ax.errorbar(
            xs, means, yerr=errors, fmt=marker, markersize=8, color=color,
            ecolor=color, elinewidth=2, capsize=0, label=series, zorder=3,
        )
        # raw labels left, AGG labels right, so they never collide
        for x, mean in zip(xs, means):
            ax.annotate(
                f"{mean:+.2%}", (x, mean), xytext=(side * 8, 0), textcoords="offset points",
                ha="left" if side > 0 else "right", va="center", fontsize=8, color=INK,
            )

    n_by_group = summary.drop_duplicates("group").set_index("group")["n"]
    ax.set_xticks(range(len(groups)))
    ax.set_xticklabels([f"{g}\nn = {n_by_group[g]}" for g in groups], color=INK)
    ax.set_xlim(-0.6, len(groups) - 0.4)
    ax.axhline(0, color=MUTED, linewidth=1, zorder=1)
    ax.yaxis.set_major_formatter(lambda y, _: f"{y:.1%}")
    ax.set_ylabel("Release day return", color=INK)
    ax.set_title("TLT on FOMC release days, raw and against AGG (95% bootstrap CI)", color=INK)
    _style_axes(ax)
    ax.legend(frameon=False, labelcolor=INK, loc="upper left")
    fig.tight_layout()

    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out

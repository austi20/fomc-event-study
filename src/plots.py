"""Figures: AAR by offset with CI bands, and the CAR distribution."""

from __future__ import annotations

from pathlib import Path

FIGURES_DIR = Path(__file__).resolve().parents[1] / "figures"


def plot_aar_by_offset(aar, out: Path = FIGURES_DIR / "aar_by_offset.png"):
    raise NotImplementedError


def plot_car_distribution(car, out: Path = FIGURES_DIR / "car_distribution.png"):
    raise NotImplementedError

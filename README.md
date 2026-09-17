# FOMC Announcement Event Study

An event study testing whether rate-sensitive equity sectors earn abnormal returns
around FOMC policy statement releases, and whether the effect is larger for regional
banks (`KRE`) than for the broad market (`SPY`).

**Headline result:** across 94 FOMC statement releases (2015-2026), long-duration
Treasuries (`TLT`) show a mean abnormal return of **+0.30%** on the announcement day
itself (95% bootstrap CI **[0.13%, 0.47%]**, t-test p = 0.001) — the one effect in
this study that survives both the t-test and the bootstrap. The hypothesized
regional-bank effect did not: KRE's mean 3-day CAR is -0.42% vs. SPY's -0.03%, and
the 95% bootstrap CI for that difference is **[-1.08%, +0.27%]**, comfortably
including zero.

**Method:** market-model event study. For each ticker and event, alpha/beta are
estimated over a `[t-250, t-30]` pre-event window (SPY itself uses a constant-mean
model rather than being regressed on itself). Abnormal returns are then computed
over a `[-1, +1]` event window and aggregated into average abnormal return (AAR)
and cumulative abnormal return (CAR). Significance is assessed with both a t-test
and a seeded 10,000-resample bootstrap.

## Timeline

| Session | Date | Scope | Status |
|---|---|---|---|
| 1 | Sep 15, 2026 | Assemble the FOMC event table | Done |
| 2 | Sep 15, 2026 | Market model + abnormal returns | Done |
| 3 | Sep 17, 2026 | Inference, figures, write-up | Done |

## Data

- `data/events.csv` — 94 FOMC statement-release dates, 2015 through the most recent
  completed meeting. Two-day meetings use the second (statement) day; the March 2020
  emergency actions are flagged `unscheduled` rather than dropped.
- `data/abnormal_returns.parquet` — one row per (ticker, event, offset): 1,128 rows
  across SPY, KRE, XLF, TLT.
- `data/aar_by_offset.csv` — average abnormal return by ticker and offset.

## Repo layout

```
src/
  fomc_dates.py    # event table (Session 1)
  returns.py       # price fetch/cache + log returns (Session 2)
  event_study.py   # market model, abnormal returns, AAR/CAR (Session 2)
  inference.py     # significance tests, bootstrap CIs (Session 3)
  plots.py         # figures (Session 3)
tests/             # pytest suite, written alongside each module
data/              # events.csv, abnormal_returns.parquet, aar_by_offset.csv
notebooks/         # end-to-end analysis notebook (Session 3)
```

## Setup

```bash
pip install -r requirements.txt
pytest
jupyter nbconvert --to notebook --execute --inplace notebooks/01_event_study.ipynb
```

The notebook re-derives everything from `data/events.csv` and the cached prices in
`data/raw/` (re-downloaded via `yfinance` on a cache miss), runs the t-tests and
bootstrap CIs, and regenerates both figures below.

## Results

![AAR by event-day offset, per ticker, with 95% bootstrap CI bands](figures/aar_by_offset.png)

![Distribution of per-event CAR, per ticker, with mean and 95% bootstrap CI marked](figures/car_distribution.png)

| Ticker | Offset-0 AAR | 95% bootstrap CI | t-test p |
|---|---|---|---|
| TLT | +0.30% | [0.13%, 0.47%] | 0.001 |
| XLF | -0.15% | [-0.30%, -0.003%] | 0.059 |
| KRE | -0.20% | [-0.55%, 0.13%] | 0.263 |
| SPY | -0.15% | [-0.51%, 0.16%] | 0.381 |

Only TLT's announcement-day reaction survives both the t-test and the bootstrap.
The headline comparison — KRE's mean 3-day CAR (-0.42%) vs. SPY's (-0.03%) — has a
95% bootstrap CI of **[-1.08%, +0.27%]** on the difference, which includes zero: no
evidence here that regional banks react more than the broad market. That null
result is itself the finding — see Limitations for why 94 events isn't a lot of
independent evidence either way.

## Limitations

- **Overlapping estimation windows.** FOMC meetings are ~6 weeks apart; the
  220-day estimation window for one event overlaps the event window of several
  neighbors, so alpha/beta draw on data that isn't independent across events.
- **Volatility clustering.** Daily returns are not i.i.d. — volatility is
  autocorrelated, so t-test and bootstrap standard errors are understated during
  volatile stretches. The bootstrap resamples across events, not within an
  event's time series, so it doesn't correct for this on its own.
- **2020 outliers.** 2 of the 94 events are unscheduled emergency actions in
  March 2020. KRE's mean CAR on those two (-1.72%) is ~4x more negative than on
  the other 92 (-0.39%) — a small enough n to be a data point rather than a
  subgroup estimate, but large enough to pull the full-sample mean.
- **Multiple testing.** 12 (ticker × offset) t-tests plus the KRE-vs-SPY
  comparison ran with no multiple-comparison correction. At uncorrected α=0.05,
  ~1 nominal "significant" result among 12 is expected by chance; TLT's result
  clears even a Bonferroni correction, but XLF's (p ≈ 0.06) would not survive any
  correction and should be read as suggestive only.

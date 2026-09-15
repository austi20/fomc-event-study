# FOMC Announcement Event Study

An event study testing whether rate-sensitive equity sectors earn abnormal returns
around FOMC policy statement releases, and whether the effect is larger for regional
banks (`KRE`) than for the broad market (`SPY`).

**Method:** market-model event study. For each ticker and event, alpha/beta are
estimated over a `[t-250, t-30]` pre-event window (SPY itself uses a constant-mean
model rather than being regressed on itself). Abnormal returns are then computed
over a `[-1, +1]` event window and aggregated into average abnormal return (AAR)
and cumulative abnormal return (CAR). Significance will be assessed with both a
t-test and a seeded bootstrap.

## Timeline

| Session | Date | Scope | Status |
|---|---|---|---|
| 1 | Sep 15, 2026 | Assemble the FOMC event table | Done |
| 2 | Sep 15, 2026 | Market model + abnormal returns | Done |
| 3 | Sep 18, 2026 | Inference, figures, write-up | Pending |

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
```

## Results

Pending Session 3 (significance tests, bootstrap confidence intervals, and figures).

## Limitations

Overlapping estimation windows across events, volatility clustering (returns are not
i.i.d.), the 2020 outliers, and multiple-comparison exposure from testing several
offsets and tickers. Addressed explicitly in the Session 3 write-up.

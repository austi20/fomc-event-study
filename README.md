# FOMC Announcement Event Study

[![tests](https://github.com/austi20/fomc-event-study/actions/workflows/tests.yml/badge.svg)](https://github.com/austi20/fomc-event-study/actions/workflows/tests.yml)

When the Fed releases a policy statement, does the market move in a way you can
actually measure? I tested that on 94 FOMC statement releases from January 2015
through July 2026 across four ETFs, using a market model event study.

**What I found.** Long dated Treasuries react, stocks mostly do not. TLT earns an
average abnormal return of **+0.30%** on the release day itself, with a 95%
bootstrap confidence interval of **[0.13%, 0.47%]** and a t test p value of
0.001. It is the only result in the study that the t test and the bootstrap both
agree on.

**What I expected and did not get.** I went in thinking regional banks would be
the story. They borrow short and lend long, so they should be the most rate
sensitive corner of the equity market. They were not. KRE averages a three day
cumulative abnormal return of -0.42% against SPY's -0.03%, and the bootstrap
interval on that difference runs from **-1.08% to +0.27%**. It contains zero, so
I cannot say the two are different. I am reporting the null result because that
is the answer the data gave, and a null result I can defend is worth more than a
significant one I cannot.

## The numbers

![Average abnormal return by event day offset, per ticker, with 95% bootstrap confidence bands](figures/aar_by_offset.png)

![Distribution of cumulative abnormal return per event, per ticker, with the mean and 95% bootstrap interval marked](figures/car_distribution.png)

Release day only, one row per ticker:

| Ticker | Average abnormal return | 95% bootstrap CI | t test p |
|---|---|---|---|
| TLT | +0.30% | [0.13%, 0.47%] | 0.001 |
| XLF | -0.15% | [-0.30%, -0.003%] | 0.059 |
| KRE | -0.20% | [-0.55%, 0.13%] | 0.263 |
| SPY | -0.15% | [-0.51%, 0.16%] | 0.381 |

SPY's row is not the same kind of number as the other three. It comes from the
constant mean model, so it is a raw move net of its own trend rather than a
market adjusted residual. It also sits at -0.149% against XLF's -0.151%, which
is why the two print identically here.

XLF is worth a second look, because the two methods disagree about it. The
bootstrap interval stops just short of zero at [-0.30%, -0.003%], which reads
like a real effect. The t test puts it at p = 0.059, which does not clear the
usual 0.05 bar. Both answers are sitting on the line, so I am not claiming it.

## How it works

Everything runs on daily log returns. That is what lets CAR be a plain sum,
since log returns add across days and simple returns do not. At the size of
these moves a log percent and a percent differ by far less than the error bars
around them, so I report them as percents.

For every ticker and every event, alpha and beta come from a market model fit on
the 221 trading days from `t-250` to `t-30`, far enough back that the
announcement itself is not in the training data. Abnormal return is then the
actual return minus what that model predicted, computed across a `[-1, +1]`
window around the release.

SPY is the market here, so regressing it on itself would be meaningless. It gets
a constant mean model instead. That is worth being explicit about, because it
means one column holds two different quantities. KRE, XLF and TLT abnormal
returns are what is left after their exposure to SPY comes out. SPY's is just
its move net of its own trailing average.

From there the abnormal returns aggregate two ways. AAR is the average across
all 94 events at a single offset, which is what the first figure plots. CAR sums
the three days of the window for one event, which is what the second figure
distributes. Significance comes from a t test and a percentile bootstrap of
10,000 resamples with a fixed seed, so the intervals reproduce exactly.

## The data

`data/events.csv` holds the 94 statement release dates, which I assembled by
hand from the Fed's published
[FOMC calendar](https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm).
Two things there are easy to get wrong and both are handled. Two day meetings
release the statement on the second day, not the first. The March 2020 emergency
intermeeting cuts are real statement releases, so they are flagged as
`unscheduled` rather than quietly dropped, and one of them landed on a Sunday
and rolls forward to the next trading day.

Prices are daily adjusted closes for SPY, KRE, XLF and TLT from `yfinance`,
pulled on 2026-09-15 and running from 2014-01-02 to that date. The event table
stops at the last statement released before that pull, which is why the sample
ends in July 2026. `data/raw/` is gitignored, so a fresh clone refills the cache
from the API the first time it runs.

That last part matters for reproducing this. Adjusted closes get revised every
time a dividend or a split lands, so a pull a year from now will not match mine
to the last decimal. `data/abnormal_returns.parquet` is committed for exactly
that reason, one row per ticker, event and offset, so anyone can check the
numbers against the ones I actually ran.

## Running it

```bash
pip install -r requirements.txt
pytest
jupyter nbconvert --to notebook --execute --inplace notebooks/01_event_study.ipynb
```

The notebook rebuilds every number and both figures from `data/events.csv` and
the price data. Nothing in it reads a precomputed result. The first run pulls
about twelve years of daily closes from `yfinance` and caches them, so it needs
a network connection once. If you would rather just read it, GitHub renders it
with the output already in place:
[notebooks/01_event_study.ipynb](notebooks/01_event_study.ipynb).

```
src/
  fomc_dates.py    # the event table
  returns.py       # price download, cache, log returns
  event_study.py   # market model, abnormal returns, AAR and CAR
  inference.py     # t tests and bootstrap intervals
  plots.py         # the two figures
tests/             # the test suite
notebooks/         # the analysis, start to finish
```

## What would break this

- **Overlapping estimation windows.** FOMC meetings sit about six weeks apart
  and the estimation window is 221 trading days, so one event's window covers
  several of its neighbors. The alphas and betas are not estimated from
  independent samples, which means their real sampling variance is wider than
  these numbers imply.
- **Volatility clustering.** Daily returns are not i.i.d. Volatile days arrive
  in clusters, so standard errors from both methods run small in exactly the
  stretches where returns are largest. The bootstrap resamples whole events
  rather than days inside an event, so it does not solve this either.
- **2020.** Two of the 94 events are the emergency cuts in March 2020. KRE's
  average CAR on those two is -1.72% against -0.39% on the other 92. With n = 2
  that is an anecdote rather than a subgroup, but it is large enough to pull the
  full sample average.
- **The KRE against SPY comparison is blunter than it looks.** KRE's abnormal
  return already has its market exposure taken out, at an average beta of 1.18.
  Subtracting SPY's abnormal return on top of that removes the market a second
  time, so what I actually tested is closer to KRE's return minus 2.18 times the
  market's than to one reaction minus another. The cleaner read on whether
  regional banks move more than their beta implies is KRE's own abnormal return,
  and that is -0.20% at p = 0.263. Same null either way, which is why the
  comparison stays in, but it is not the sharp instrument the framing suggests.
- **Multiple testing.** I ran 12 t tests, one per ticker and offset, plus the
  KRE against SPY comparison, with no correction applied. At an uncorrected 0.05
  threshold about one apparent hit in 12 turns up by luck alone. TLT at p = 0.001
  clears a Bonferroni threshold anyway. XLF at p = 0.059 clears nothing.

## What I would do next

Widen the event window past three days and see whether the KRE effect shows up
slower than I assumed. Split the sample by whether the decision surprised the
market, using fed funds futures to measure the surprise, since pooling hikes,
cuts and holds together averages real reactions toward zero. Both are bigger
jobs than this one was.

## License

MIT.

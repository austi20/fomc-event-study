# FOMC Announcement Event Study

**Type:** sprint project · **Estimated effort:** 6–8 hrs over 3 working sessions · **Due:** Friday, September 18, 2026

---

## Background: why this project helps your career goals

You are targeting data analytics internships in **financial services and AI**. Your current portfolio
pipeline is strong on *engineering* (the SEC EDGAR analyzer: APIs, caching, XBRL parsing) and on
*BI* (the PL-300 track). The gap a finance recruiter will probe in an interview is **statistical
inference** — can you set up a hypothesis, control for confounders, and say honestly how confident
you are in a number?

An **event study** is the canonical answer. It is the single most common applied-statistics method
in finance research, it is used inside asset managers and at the Fed, and it is small enough to
finish in three sessions. It also gives you something unusual on a student resume: a claim with a
confidence interval attached, rather than an accuracy score on a tutorial dataset.

**The question:** On days the FOMC releases a policy statement, do rate-sensitive equity sectors
earn abnormal returns that differ from zero — and is the effect larger for regional banks (KRE)
than for the broad market (SPY)?

This is not a tutorial clone. There is no canned dataset. You assemble the event dates from the
Federal Reserve's own calendar and the returns from a market data source, and the answer is not
written down anywhere for you to check against.

---

## Skills and tools it covers

Deliberately chosen to **not overlap** your other active items:

| Skill | Where it shows up here | Already covered elsewhere? |
|---|---|---|
| **Statistics & experiment design** | Market-model estimation, abnormal returns, t-tests, bootstrap CIs, multiple-comparison awareness | No — this is the gap |
| Event-study methodology | Estimation window vs. event window, CAR/AAR aggregation | No |
| Data assembly from a primary source | Parsing the Fed's published calendar into a clean event table | Partly (EDGAR), different source shape |
| Reproducible analysis | Notebook + `src/` module split, pinned requirements, seeded bootstrap | Reinforces |

Tools: Python, pandas, numpy, scipy/statsmodels, matplotlib, `yfinance` (or FRED), Jupyter, git.

> SEC EDGAR analyzer = data engineering + LLM. PL-300 = BI/dashboarding.
> This one = **statistics and experiment design**. No repeat.

---

## Verified resources

| Resource | URL | What you use it for |
|---|---|---|
| FOMC meeting calendars (2021–2027 + historical archive) | https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm | The event dates. Page last updated 2026-08-19; lists each meeting and the statement-release date. |
| FRED API documentation | https://fred.stlouisfed.org/docs/api/fred/ | Optional: rate series (e.g. `DFF`, `DGS2`, `DGS10`) via the `fred/series/observations` endpoint |
| FRED API key request | https://fred.stlouisfed.org/docs/api/api_key.html | Create a free FRED account first, then request the key from your account portal |
| `yfinance` on PyPI (v1.7.0, Apache-2.0) | https://pypi.org/project/yfinance/ | Daily OHLC for SPY, KRE, XLF, TLT and any peers |

All four links were fetched and confirmed live on 2026-09-14.

---

## Step-by-step plan

### Session 1 — Scaffold + build the event table (Tue Sept 16… run Tue 9/15, ~2 hrs)

1. `git init` a public repo named **`fomc-event-study`**. Add `README.md`, `requirements.txt`
   (pinned), `.gitignore` (ignore `data/raw/`), `src/`, and `notebooks/`.
2. Build `src/fomc_dates.py`. Assemble the **statement-release dates** for FOMC meetings from
   2015 through the most recent completed meeting. Two-day meetings release the statement on the
   **second** day — get this right, it is the most common error in student event studies.
3. Write the result to `data/events.csv` with columns `date`, `meeting_type` (scheduled /
   unscheduled), `is_press_conference`. Commit the CSV so the analysis is reproducible.
4. Sanity-check the count. Eight scheduled meetings per year is the baseline; unscheduled
   intermeeting actions (2020 is the obvious case) are extra and should be flagged, not dropped.

**Done when:** `data/events.csv` exists in the repo with ~90+ dated events and a row count you can
defend out loud.

---

### Session 2 — Returns + the market model (Wed 9/16, ~2.5 hrs)

1. Pull daily adjusted closes for **SPY, KRE, XLF, TLT** from 2014-01-01 to today with `yfinance`.
   Cache to `data/raw/`. Convert to log returns.
2. For each ticker and each event, estimate the **market model** on the estimation window
   `[t-250, t-30]`: regress the ticker's return on SPY's return (for SPY itself, use a constant-mean
   model instead — do not regress a series on itself).
3. Compute the **abnormal return** `AR_t = r_t - (α + β·r_market,t)` for the event window
   `[-1, +1]`, and the **cumulative abnormal return (CAR)** across that window.
4. Store a tidy `data/abnormal_returns.parquet`: one row per (ticker, event_date, offset).

**Done when:** you can produce a table of average abnormal return (AAR) by offset for each ticker.

> Sequencing note: CSE 440 Homework 1 is due Wed 9/16 at 11:59 AM ET. Do this session in the
> afternoon, after that is submitted.

---

### Session 3 — Inference, write-up, publish (Fri 9/18, ~2.5 hrs)

1. Test **AAR ≠ 0** at each offset with a one-sample t-test, then redo it with a **bootstrap**
   (10,000 resamples, seeded) and report the 95% CI. Say plainly where the two disagree.
2. Test the headline comparison: is KRE's mean CAR larger than SPY's? Two-sample test plus a
   bootstrap difference-in-means CI.
3. Acknowledge the obvious threats in writing: overlapping estimation windows, volatility
   clustering (returns are not i.i.d.), the 2020 outliers, and the fact that you ran several tests.
   A paragraph naming these is worth more in an interview than a lower p-value.
4. Produce **two figures**: (a) AAR by event-day offset with CI bands, per ticker; (b) the
   distribution of CARs with the mean and CI marked.
5. Write the repo README: question, data, method, result **with the number**, limitations. Push,
   and add the repo to https://austi20.github.io/portfolio/.

**Done when:** the repo is public, the notebook runs top to bottom from a clean checkout, and the
README's headline sentence contains a number and an interval.

---

## Deliverables and how to showcase them

1. **Public GitHub repo** — `github.com/austi20/fomc-event-study`, with a real README (not a stub),
   pinned `requirements.txt`, and a notebook that runs end to end.
2. **Portfolio entry** on austi20.github.io/portfolio/ — lead with the finding and one figure.
3. **Suggested resume bullet** (fill in your actual numbers once Session 3 is done):

   > Ran an event study on 90+ FOMC statement releases (2015–2026) across four ETFs, estimating
   > market-model abnormal returns over a 3-day window; found a mean cumulative abnormal return of
   > **X.XX%** for regional banks (95% bootstrap CI **[A, B]**), **N.N×** the broad-market effect.

4. **Interview talking point** — you will get asked "how do you know that's real?" Your answer is
   the estimation window, the bootstrap, and the limitations paragraph. Rehearse it.

---

## Estimated hours and due date

| | |
|---|---|
| Total effort | 6–8 hours |
| Sessions | 3 (Tue 9/15, Wed 9/16, Fri 9/18) |
| **Due** | **Friday, September 18, 2026** |

This lands well before the late-October interview-readiness target, and the class week it sits in
is light: CSE 440 HW1 (Wed 9/16) and STT 442 HW1 group component (Thu 9/17), no exams. Thursday is
deliberately left free of sessions for the STT group work.

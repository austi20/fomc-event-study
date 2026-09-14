"""Tests for the FOMC event table assembly."""

import pandas as pd
import pytest

from src.fomc_dates import COLUMNS, build_events


@pytest.fixture(scope="module")
def events() -> pd.DataFrame:
    return build_events()


def test_columns_match_spec(events):
    assert list(events.columns) == COLUMNS


def test_row_count_is_at_least_90(events):
    assert len(events) >= 90


def test_dates_are_unique_and_sorted(events):
    dates = pd.to_datetime(events["date"])
    assert dates.is_monotonic_increasing
    assert dates.is_unique


def test_only_2015_onward_by_default(events):
    assert events["date"].min() >= "2015-01-01"


def test_start_year_filters_earlier_meetings():
    filtered = build_events(start_year=2020)
    assert filtered["date"].min() >= "2020-01-01"
    assert len(filtered) < len(build_events(start_year=2015))


def test_two_day_meeting_uses_second_day(events):
    # 2015-03-17/18 FOMC meeting: statement released the second day.
    assert "2015-03-17" not in set(events["date"])
    assert "2015-03-18" in set(events["date"])


def test_march_2020_emergency_actions_flagged_unscheduled(events):
    by_date = events.set_index("date")["meeting_type"]
    assert by_date["2020-03-03"] == "unscheduled"
    assert by_date["2020-03-15"] == "unscheduled"


def test_meeting_type_is_scheduled_or_unscheduled(events):
    assert set(events["meeting_type"]) <= {"scheduled", "unscheduled"}


def test_press_conference_every_meeting_from_2019(events):
    post_2019 = events[events["date"] >= "2019-01-01"]
    assert post_2019["is_press_conference"].all()


def test_press_conference_not_every_meeting_before_2019(events):
    pre_2019 = events[events["date"] < "2019-01-01"]
    assert not pre_2019["is_press_conference"].all()
    assert pre_2019["is_press_conference"].any()

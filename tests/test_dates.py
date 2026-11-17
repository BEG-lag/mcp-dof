from datetime import date, timedelta

import pytest

from mcp_dof.dates import (
    DateError,
    from_sidof,
    iter_days,
    parse_date,
    parse_range,
    to_sidof,
    today_mx,
)


@pytest.mark.parametrize(
    "text",
    ["2026-11-13", "13-11-2026", "13/11/2026", "13.11.2026", " 2026-11-13 "],
)
def test_parse_date_accepts_common_formats(text: str) -> None:
    assert parse_date(text) == date(2026, 11, 13)


@pytest.mark.parametrize("text", [None, "", "today", "HOY", "now"])
def test_parse_date_today_aliases(text: str | None) -> None:
    assert parse_date(text) == today_mx()


@pytest.mark.parametrize("text", ["yesterday", "ayer"])
def test_parse_date_yesterday_aliases(text: str) -> None:
    assert parse_date(text) == today_mx() - timedelta(days=1)


def test_parse_date_accepts_date_objects() -> None:
    assert parse_date(date(2025, 1, 2)) == date(2025, 1, 2)


@pytest.mark.parametrize("text", ["13 de noviembre", "2026/11/13", "11-2026", "tomorrow"])
def test_parse_date_rejects_unknown_formats_with_a_hint(text: str) -> None:
    with pytest.raises(DateError, match="YYYY-MM-DD"):
        parse_date(text)


def test_parse_date_rejects_impossible_dates() -> None:
    with pytest.raises(DateError, match=r"month must be in 1\.\.12"):
        parse_date("2026-13-01")


def test_parse_date_rejects_future_dates() -> None:
    future = today_mx() + timedelta(days=1)
    with pytest.raises(DateError, match="future"):
        parse_date(future.isoformat())


def test_parse_date_rejects_dates_before_the_dof_archive() -> None:
    with pytest.raises(DateError, match="before 1917"):
        parse_date("1916-12-31")


def test_parse_range_defaults_to_last_n_days() -> None:
    start, end = parse_range(None, "2026-11-13", default_days=30, max_days=92)
    assert end == date(2026, 11, 13)
    assert (end - start).days == 29


def test_parse_range_rejects_inverted_ranges() -> None:
    with pytest.raises(DateError, match="Swap them"):
        parse_range("2026-11-13", "2026-11-01", default_days=30, max_days=92)


def test_parse_range_enforces_the_maximum_span() -> None:
    with pytest.raises(DateError, match="maximum is 92"):
        parse_range("2026-01-01", "2026-11-13", default_days=30, max_days=92)


def test_iter_days_both_directions() -> None:
    start, end = date(2026, 11, 13), date(2026, 11, 15)
    assert list(iter_days(start, end)) == [start, date(2026, 11, 14), end]
    assert next(iter(iter_days(start, end, newest_first=True))) == end


def test_sidof_format_round_trip() -> None:
    assert to_sidof(date(2026, 1, 5)) == "05-01-2026"
    assert from_sidof("05-01-2026") == date(2026, 1, 5)

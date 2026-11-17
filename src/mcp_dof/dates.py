"""Date parsing and validation.

The DOF is published in Mexico City, so "today" always means today in
``America/Mexico_City``, regardless of where the server runs. SIDOF expects
dates as ``DD-MM-YYYY``; users and models usually type ISO dates. This module
accepts both and fails with a message that tells the caller how to fix it.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

MX_TZ = ZoneInfo("America/Mexico_City")

# SIDOF indexes go back to 1917; full texts are only available for recent decades.
EARLIEST = date(1917, 1, 1)

_TODAY = {"today", "hoy", "now"}
_YESTERDAY = {"yesterday", "ayer"}

_ISO = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
_DMY = re.compile(r"^(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})$")


class DateError(ValueError):
    """Raised when a user supplied date cannot be used."""


def today_mx() -> date:
    """Return today's date in Mexico City."""
    return datetime.now(MX_TZ).date()


def parse_date(value: str | date | None, *, field: str = "date") -> date:
    """Parse ``value`` into a :class:`date`, validating the DOF range.

    Accepted inputs: ``None`` or ``""`` (today), ``"today"``/``"hoy"``,
    ``"yesterday"``/``"ayer"``, ``YYYY-MM-DD``, ``DD-MM-YYYY`` and ``DD/MM/YYYY``.
    """
    if isinstance(value, datetime):
        value = value.date()
    if isinstance(value, date):
        parsed = value
    else:
        text = (value or "").strip().lower()
        if not text or text in _TODAY:
            parsed = today_mx()
        elif text in _YESTERDAY:
            parsed = today_mx() - timedelta(days=1)
        else:
            parsed = _parse_text(text, field)

    if parsed < EARLIEST:
        raise DateError(f"{field} {parsed.isoformat()} is before {EARLIEST.isoformat()}.")
    if parsed > today_mx():
        raise DateError(
            f"{field} {parsed.isoformat()} is in the future (today in Mexico City is "
            f"{today_mx().isoformat()})."
        )
    return parsed


def _parse_text(text: str, field: str) -> date:
    if match := _ISO.match(text):
        year, month, day = (int(g) for g in match.groups())
    elif match := _DMY.match(text):
        day, month, year = (int(g) for g in match.groups())
    else:
        raise DateError(
            f"Invalid {field} {text!r}. Use YYYY-MM-DD (for example 2026-11-13), "
            "DD-MM-YYYY, 'today' or 'yesterday'."
        )
    try:
        return date(year, month, day)
    except ValueError as exc:
        raise DateError(f"Invalid {field} {text!r}: {exc}.") from exc


def parse_range(
    date_from: str | date | None,
    date_to: str | date | None,
    *,
    default_days: int,
    max_days: int,
) -> tuple[date, date]:
    """Parse an inclusive date range, defaulting to the last ``default_days`` days."""
    end = parse_date(date_to, field="date_to")
    if date_from in (None, ""):
        start = max(EARLIEST, end - timedelta(days=default_days - 1))
    else:
        start = parse_date(date_from, field="date_from")
    if start > end:
        raise DateError(
            f"date_from {start.isoformat()} is after date_to {end.isoformat()}. Swap them."
        )
    span = (end - start).days + 1
    if span > max_days:
        raise DateError(
            f"The range {start.isoformat()} to {end.isoformat()} covers {span} days; the "
            f"maximum is {max_days}. Narrow it or split the query into several calls."
        )
    return start, end


def iter_days(start: date, end: date, *, newest_first: bool = False) -> Iterator[date]:
    """Yield every day in the inclusive range."""
    span = (end - start).days
    offsets = range(span, -1, -1) if newest_first else range(span + 1)
    for offset in offsets:
        yield start + timedelta(days=offset)


def to_sidof(day: date) -> str:
    """Format a date the way SIDOF URLs expect it (``DD-MM-YYYY``)."""
    return day.strftime("%d-%m-%Y")


def from_sidof(text: str) -> date:
    """Parse a SIDOF ``DD-MM-YYYY`` date."""
    return datetime.strptime(text, "%d-%m-%Y").date()

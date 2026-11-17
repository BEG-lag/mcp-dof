"""Async client for the public SIDOF API (Secretaría de Gobernación).

Design goals, in order: be polite to a government server, be predictable for an
LLM caller, and be easy to test offline.

* One shared :class:`httpx.AsyncClient` with explicit timeouts.
* A minimum interval between requests (default 250 ms) enforced with a lock.
* Retries with exponential backoff and jitter on network errors, 429 and 5xx,
  honouring ``Retry-After`` when the server sends it.
* An in-memory TTL cache: past editions are effectively immutable, so they are
  cached for hours; today's edition and indicators expire in minutes.
"""

from __future__ import annotations

import asyncio
import random
import time
from collections import OrderedDict
from datetime import date, timedelta
from typing import Any

import httpx

from . import __version__
from .dates import to_sidof, today_mx
from .models import (
    DAILY_INDICATORS,
    SIDOF_API,
    DayIndex,
    IndicatorValue,
    NoteDetail,
    parse_day,
    parse_indicators,
    parse_note_detail,
)

USER_AGENT = f"mcp-dof/{__version__} (+https://github.com/BEG-lag/mcp-dof)"

RETRY_STATUS = {429, 500, 502, 503, 504}


class SidofError(RuntimeError):
    """SIDOF could not be reached or answered with an error."""


class NoteNotFoundError(SidofError):
    """The requested note code does not exist."""


class TTLCache:
    """A tiny LRU cache with per-entry expiry. Not thread safe; fine for asyncio."""

    def __init__(self, max_entries: int = 512) -> None:
        self._data: OrderedDict[str, tuple[float, Any]] = OrderedDict()
        self.max_entries = max_entries

    def get(self, key: str) -> Any | None:
        item = self._data.get(key)
        if item is None:
            return None
        expires, value = item
        if expires < time.monotonic():
            del self._data[key]
            return None
        self._data.move_to_end(key)
        return value

    def set(self, key: str, value: Any, ttl: float) -> None:
        self._data[key] = (time.monotonic() + ttl, value)
        self._data.move_to_end(key)
        while len(self._data) > self.max_entries:
            self._data.popitem(last=False)

    def clear(self) -> None:
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)


def _day_ttl(day: date) -> float:
    """Recent editions can still change (late vespertinas, extraordinarias)."""
    age = (today_mx() - day).days
    if age <= 1:
        return 5 * 60
    if age <= 7:
        return 60 * 60
    return 12 * 60 * 60


class SidofClient:
    def __init__(
        self,
        *,
        base_url: str = SIDOF_API,
        timeout: float = 20.0,
        max_retries: int = 3,
        backoff: float = 0.75,
        min_interval: float = 0.25,
        transport: httpx.AsyncBaseTransport | None = None,
        cache: TTLCache | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.backoff = backoff
        self.min_interval = min_interval
        self.cache = cache if cache is not None else TTLCache()
        self.requests_made = 0
        self._http = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=10.0),
            # SIDOF answers 406 to a bare "Accept: application/json"; keep the wildcard.
            headers={"User-Agent": USER_AGENT, "Accept": "application/json, */*;q=0.8"},
            transport=transport,
            follow_redirects=True,
        )
        self._lock = asyncio.Lock()
        self._last_request = 0.0

    async def aclose(self) -> None:
        await self._http.aclose()

    async def __aenter__(self) -> SidofClient:
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.aclose()

    # ------------------------------------------------------------------ HTTP

    async def _throttle(self) -> None:
        async with self._lock:
            wait = self._last_request + self.min_interval - time.monotonic()
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request = time.monotonic()

    async def get_json(self, path: str, *, ttl: float) -> dict[str, Any]:
        """GET ``{base_url}/{path}`` and return the decoded JSON object (cached)."""
        url = f"{self.base_url}/{path.lstrip('/')}"
        cached = self.cache.get(url)
        if cached is not None:
            return cached

        last_error = "unknown error"
        retry_after: float | None = None
        for attempt in range(self.max_retries + 1):
            if attempt:
                await asyncio.sleep(self._delay(attempt, retry_after))
                retry_after = None
            await self._throttle()
            try:
                response = await self._http.get(url)
                self.requests_made += 1
            except httpx.TransportError as exc:
                last_error = f"{type(exc).__name__}: {exc}"
                continue
            if response.status_code in RETRY_STATUS:
                last_error = f"HTTP {response.status_code}"
                retry_after = _retry_after(response)
                continue
            if response.status_code >= 400:
                raise SidofError(f"SIDOF answered HTTP {response.status_code} for {url}")
            try:
                payload = response.json()
            except ValueError as exc:
                raise SidofError(f"SIDOF returned invalid JSON for {url}") from exc
            if not isinstance(payload, dict):
                raise SidofError(f"Unexpected SIDOF payload for {url}")
            self.cache.set(url, payload, ttl)
            return payload

        raise SidofError(
            f"SIDOF is not responding ({last_error}) after {self.max_retries + 1} attempts: {url}. "
            "The government server is sometimes slow; try again in a few minutes."
        )

    def _delay(self, attempt: int, retry_after: float | None) -> float:
        if retry_after is not None:
            return min(retry_after, 30.0)
        return self.backoff * (2 ** (attempt - 1)) + random.uniform(0, self.backoff / 2)

    # ------------------------------------------------------------- Endpoints

    async def day_index(self, day: date) -> DayIndex:
        """Table of contents for every edition published on ``day``."""
        payload = await self.get_json(f"notas/{to_sidof(day)}", ttl=_day_ttl(day))
        return parse_day(payload, day)

    async def note(self, code: int) -> NoteDetail:
        """A single note, including its HTML body."""
        payload = await self.get_json(f"notas/nota/{code}", ttl=6 * 60 * 60)
        detail = parse_note_detail(payload)
        if detail is None:
            raise NoteNotFoundError(f"There is no DOF note with code {code}.")
        return detail

    async def indicators(self, day: date) -> list[IndicatorValue]:
        """Indicators (exchange rate, UDIS, TIIE) published for ``day``."""
        ttl = 30 * 60 if (today_mx() - day).days <= 1 else 12 * 60 * 60
        payload = await self.get_json(f"indicadores/{to_sidof(day)}", ttl=ttl)
        return parse_indicators(payload)

    async def latest_indicators(
        self, day: date, *, lookback_days: int = 10
    ) -> list[IndicatorValue]:
        """The latest value of each daily indicator published on or before ``day``.

        UDIS are published for every calendar day, while the FIX exchange rate and the
        TIIE only appear on business days, so a weekend date is completed with the most
        recent earlier publication of each indicator.
        """
        found: dict[int, IndicatorValue] = {}
        for offset in range(lookback_days + 1):
            for value in await self.indicators(day - timedelta(days=offset)):
                found.setdefault(value.type_code, value)
            if all(code in found for code in DAILY_INDICATORS):
                break
        order = {code: i for i, code in enumerate(DAILY_INDICATORS)}
        return sorted(found.values(), key=lambda v: (order.get(v.type_code, 99), v.type_code))

    async def indicator_series(
        self, type_code: int, start: date, end: date
    ) -> list[IndicatorValue]:
        """Every published value of one indicator between two dates (inclusive)."""
        path = f"indicadores/{type_code}/{to_sidof(start)}/{to_sidof(end)}"
        payload = await self.get_json(path, ttl=_day_ttl(end))
        return sorted(parse_indicators(payload), key=lambda v: v.day)


def _retry_after(response: httpx.Response) -> float | None:
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        return None

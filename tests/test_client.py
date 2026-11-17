from datetime import date

import httpx
import pytest

from mcp_dof.client import USER_AGENT, NoteNotFoundError, SidofClient, SidofError, TTLCache

pytestmark = pytest.mark.anyio


async def test_day_index_uses_sidof_date_format_and_user_agent(sidof, fake_sidof) -> None:
    index = await sidof.day_index(date(2026, 11, 13))
    assert len(index.notes) == 66
    request = fake_sidof.requests[0]
    assert request.url.path == "/dof/sidof/notas/13-11-2026"
    assert request.headers["User-Agent"] == USER_AGENT
    assert "*/*" in request.headers["Accept"]  # a bare application/json gets HTTP 406


async def test_responses_are_cached(sidof, fake_sidof) -> None:
    await sidof.day_index(date(2026, 11, 13))
    await sidof.day_index(date(2026, 11, 13))
    assert fake_sidof.paths() == ["notas/13-11-2026"]
    assert sidof.requests_made == 1


async def test_transient_errors_are_retried(sidof, fake_sidof) -> None:
    fake_sidof.overrides["notas/13-11-2026"] = [
        httpx.Response(503),
        httpx.Response(502, headers={"Retry-After": "0"}),
    ]
    index = await sidof.day_index(date(2026, 11, 13))
    assert len(index.notes) == 66
    assert fake_sidof.paths() == ["notas/13-11-2026"] * 3


async def test_gives_up_after_max_retries(make_client, fake_sidof) -> None:
    fake_sidof.overrides["notas/13-11-2026"] = [httpx.Response(500)] * 10
    async with make_client(max_retries=2) as client:
        with pytest.raises(SidofError, match="after 3 attempts"):
            await client.day_index(date(2026, 11, 13))
    assert len(fake_sidof.requests) == 3


async def test_network_errors_are_retried() -> None:
    calls = 0

    def flaky(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            raise httpx.ConnectTimeout("slow", request=request)
        return httpx.Response(200, json={"Nota": []})

    client = SidofClient(transport=httpx.MockTransport(flaky), min_interval=0, backoff=0)
    with pytest.raises(NoteNotFoundError):
        await client.note(1)
    assert calls == 2
    await client.aclose()


async def test_client_errors_are_not_retried(sidof, fake_sidof) -> None:
    with pytest.raises(SidofError, match="HTTP 404"):
        await sidof.get_json("does/not/exist", ttl=1)
    assert len(fake_sidof.requests) == 1


async def test_note_not_found(sidof) -> None:
    with pytest.raises(NoteNotFoundError, match="9999999"):
        await sidof.note(9999999)


async def test_weekend_indicators_fall_back_per_indicator(sidof) -> None:
    values = await sidof.latest_indicators(date(2026, 11, 15))
    by_key = {v.type.key: v for v in values if v.type}
    assert by_key["udis"].day == date(2026, 11, 15)  # UDIS are published every day
    assert by_key["usd"].day == date(2026, 11, 13)  # FIX only on business days
    assert list(by_key)[:2] == ["usd", "udis"]


async def test_indicator_series_sorted_by_date(sidof) -> None:
    values = await sidof.indicator_series(158, date(2026, 11, 1), date(2026, 11, 13))
    assert len(values) == 9
    assert values[0].day < values[-1].day


def test_ttl_cache_expiry_and_lru() -> None:
    cache = TTLCache(max_entries=2)
    cache.set("a", 1, ttl=60)
    cache.set("b", 2, ttl=60)
    cache.get("a")
    cache.set("c", 3, ttl=60)  # evicts b, the least recently used
    assert cache.get("b") is None
    assert cache.get("a") == 1
    cache.set("d", 4, ttl=-1)
    assert cache.get("d") is None

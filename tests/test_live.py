"""Smoke tests against the real SIDOF API. Opt in with ``pytest --live``."""

from datetime import timedelta

import pytest

from mcp_dof.client import SidofClient
from mcp_dof.dates import today_mx
from mcp_dof.markdown import html_to_markdown

pytestmark = [pytest.mark.live, pytest.mark.anyio]


async def test_recent_business_day_has_an_edition() -> None:
    async with SidofClient() as client:
        for offset in range(10):
            index = await client.day_index(today_mx() - timedelta(days=offset))
            if index.notes:
                break
        assert index.notes, "no DOF edition found in the last 10 days"
        assert all(n.official_url.startswith("https://dof.gob.mx/") for n in index.notes)


async def test_known_note_full_text() -> None:
    async with SidofClient() as client:
        note = await client.note(5803775)
    assert note.html
    assert "Banco de México" in html_to_markdown(note.html)


async def test_latest_indicators_include_the_exchange_rate() -> None:
    async with SidofClient() as client:
        values = await client.latest_indicators(today_mx())
    keys = {v.type.key for v in values if v.type}
    assert {"usd", "udis", "tiie28"} <= keys

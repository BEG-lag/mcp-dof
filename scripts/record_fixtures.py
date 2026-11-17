"""Record SIDOF responses used by the offline test suite.

Run from the repository root:

    uv run python scripts/record_fixtures.py

Fixtures are stored verbatim (pretty printed) under tests/fixtures/, one file per
API path with "/" replaced by "__". Re-recording is only needed when SIDOF changes
its payloads; tests never touch the network.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import httpx

from mcp_dof.client import USER_AGENT
from mcp_dof.models import SIDOF_API

FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"

PATHS = [
    # A business week around a holiday (2026-11-16, Revolution Day observed).
    "notas/11-11-2026",
    "notas/12-11-2026",
    "notas/13-11-2026",
    "notas/14-11-2026",
    "notas/15-11-2026",
    "notas/16-11-2026",
    # Short notes with full HTML, and a code that does not exist.
    "notas/nota/5803775",
    "notas/nota/5803776",
    "notas/nota/9999999",
    # Indicators: a Friday, a Saturday, a Sunday, and a one-indicator range.
    "indicadores/13-11-2026",
    "indicadores/14-11-2026",
    "indicadores/15-11-2026",
    "indicadores/158/01-11-2026/13-11-2026",
]


def fixture_name(path: str) -> str:
    return path.strip("/").replace("/", "__") + ".json"


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json, */*;q=0.8"}
    with httpx.Client(timeout=30, headers=headers) as client:
        for path in PATHS:
            response = client.get(f"{SIDOF_API}/{path}")
            response.raise_for_status()
            target = FIXTURES / fixture_name(path)
            target.write_text(
                json.dumps(response.json(), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
            )
            print(f"{response.status_code} {path} -> {target.name} ({target.stat().st_size:,} B)")
            time.sleep(0.5)


if __name__ == "__main__":
    main()

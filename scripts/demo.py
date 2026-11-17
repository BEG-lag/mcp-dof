"""Run the real server over stdio and record a transcript of tool calls.

    uv run python scripts/demo.py            # prints the transcript
    uv run python scripts/demo.py --write    # also writes docs/demo.md

This is a genuine MCP round trip (client -> stdio -> mcp-dof -> SIDOF), so the
output in docs/demo.md is exactly what an MCP client such as Claude receives.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from mcp_dof.dates import today_mx

DOCS = Path(__file__).resolve().parent.parent / "docs" / "demo.md"

CALLS: list[tuple[str, dict]] = [
    ("list_edition", {"date": "2026-11-13"}),
    (
        "search_notes",
        {"practice_area": "hidrocarburos", "date_from": "2026-10-01", "date_to": "2026-11-13"},
    ),
    ("get_note", {"code": 5803775}),
    ("get_indicators", {"date": "2026-11-17"}),
    (
        "get_indicator_history",
        {"indicator": "usd", "date_from": "2026-11-01", "date_to": "2026-11-17"},
    ),
]


async def run() -> list[str]:
    transport = StdioTransport(command=sys.executable, args=["-m", "mcp_dof.server"])
    sections: list[str] = []
    async with Client(transport) as client:
        tools = await client.list_tools()
        names = ", ".join(f"`{t.name}`" for t in tools)
        sections.append(f"## tools/list\n\n{names}\n")
        for name, arguments in CALLS:
            started = time.perf_counter()
            result = await client.call_tool(name, arguments, raise_on_error=False)
            elapsed = time.perf_counter() - started
            text = result.content[0].text
            args = json.dumps(arguments, ensure_ascii=False)
            sections.append(
                f"## {name}\n\n`{args}` · {elapsed:.1f} s · "
                f"{'error' if result.is_error else 'ok'}\n\n````markdown\n{text.rstrip()}\n````\n"
            )
            print(f"\n=== {name} {args} ({elapsed:.2f}s)\n{text}")
    return sections


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write docs/demo.md")
    args = parser.parse_args()
    sections = asyncio.run(run())
    if args.write:
        header = (
            "# Demo transcript\n\n"
            f"Recorded on {today_mx().isoformat()} with `uv run python scripts/demo.py --write`: "
            "a real MCP client talking to `mcp-dof` over stdio, which queries the live SIDOF "
            "API. Nothing below was edited. Timings include network latency and a cold cache.\n\n"
        )
        DOCS.write_text(header + "\n".join(sections), encoding="utf-8")
        print(f"\nwrote {DOCS}")


if __name__ == "__main__":
    main()

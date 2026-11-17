"""Start an mcp-dof command over stdio and check the MCP handshake.

    uv run python scripts/smoke_stdio.py                     # python -m mcp_dof.server
    uv run python scripts/smoke_stdio.py -- docker run -i --rm ghcr.io/beg-lag/mcp-dof:1.0.0

CI and the release workflow use it to prove that a built container starts, speaks MCP over
stdio, reports the same version as this checkout and exposes every tool. No SIDOF request is
made, so it works offline.
"""

from __future__ import annotations

import argparse
import asyncio
import sys

from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from mcp_dof import __version__

EXPECTED_TOOLS = {
    "list_edition",
    "get_note",
    "search_notes",
    "get_indicators",
    "get_indicator_history",
}


async def check(command: list[str]) -> list[str]:
    transport = StdioTransport(command=command[0], args=command[1:])
    async with Client(transport) as client:
        info = client.server_info
        tools = {tool.name for tool in await client.list_tools()}
        prompts = {prompt.name for prompt in await client.list_prompts()}
    problems = []
    if info.name != "dof":
        problems.append(f"server name is {info.name!r}, expected 'dof'")
    if info.version != __version__:
        problems.append(f"server version is {info.version!r}, expected {__version__!r}")
    if missing := EXPECTED_TOOLS - tools:
        problems.append(f"missing tools: {', '.join(sorted(missing))}")
    if "regulatory_digest" not in prompts:
        problems.append("missing prompt: regulatory_digest")
    print(f"{info.name} {info.version}: {len(tools)} tools ({', '.join(sorted(tools))})")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", nargs="*", help="Command that starts the server over stdio.")
    args = parser.parse_args()
    command = args.command or [sys.executable, "-m", "mcp_dof.server"]
    problems = asyncio.run(check(command))
    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

"""Start the real entry point over stdio, the way Claude Desktop/Code do."""

import sys

import pytest
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

from mcp_dof import __version__

pytestmark = pytest.mark.anyio


async def test_stdio_handshake_lists_tools() -> None:
    transport = StdioTransport(command=sys.executable, args=["-m", "mcp_dof.server"])
    async with Client(transport) as client:
        assert client.server_info.name == "dof"
        assert client.server_info.version == __version__
        names = {tool.name for tool in await client.list_tools()}
    assert "list_edition" in names

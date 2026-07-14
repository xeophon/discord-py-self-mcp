"""Discord selfbot MCP integration.

Tools are auto-discovered from a local stdio MCP server backed by
discord.py-self.  Usage in the kernel:

    import discord_py_self
    guilds = await discord_py_self.list_guilds()
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from contextlib import AsyncExitStack

from dotenv import load_dotenv

from rlm import McpIntegration

__all__ = ["DiscordPySelf", "discord_py_self"]

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class DiscordPySelf(McpIntegration):
    """Discord MCP integration via a local stdio server (discord.py-self)."""

    server = "discord-py-self"
    url = None  # stdio, not HTTP

    async def _open_session(self, stack: AsyncExitStack):
        """Open an MCP ClientSession over stdio transport."""
        from mcp import ClientSession  # noqa: PLC0415
        from mcp.client.stdio import StdioServerParameters, stdio_client  # noqa: PLC0415

        if not os.environ.get("DISCORD_TOKEN"):
            raise RuntimeError(
                "DISCORD_TOKEN is not set. Put it in a .env file or export it."
            )
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "discord_py_self.server"],
        )
        read, write = await stack.enter_async_context(stdio_client(params))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        return session


discord_py_self = DiscordPySelf()

_RESERVED = {"run", "__wrapped__", "__call__"}


def __getattr__(name: str):
    if name.startswith("_") or name in _RESERVED:
        raise AttributeError(name)
    return getattr(discord_py_self, name)

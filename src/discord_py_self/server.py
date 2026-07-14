"""Read-only Discord MCP server using discord.py-self.

Run as a module:  python -m discord_py_self.server
"""

import asyncio
import importlib
import inspect
import json
import os
import sys

import discord
from google.protobuf import json_format
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

# ── protobuf compat shim (discord.py-self expects the old kwarg name) ────────
if (
    "including_default_value_fields"
    not in inspect.signature(json_format.MessageToDict).parameters
):
    original_message_to_dict = json_format.MessageToDict

    def message_to_dict(message, **kwargs):
        if "including_default_value_fields" in kwargs:
            kwargs["always_print_fields_with_no_presence"] = kwargs.pop(
                "including_default_value_fields"
            )
        return original_message_to_dict(message, **kwargs)

    importlib.import_module("discord.settings").MessageToDict = message_to_dict


def reply(message):
    return [TextContent(type="text", text=message)]


def tool(name, description, properties=None, required=None):
    return Tool(
        name=name,
        description=description,
        inputSchema={
            "type": "object",
            "properties": properties or {},
            "required": required or [],
        },
    )


def format_message(message):
    parts = [getattr(message, "clean_content", None) or message.content or ""]
    parts += [
        f"[embed] {json.dumps(embed.to_dict(), ensure_ascii=False)}"
        for embed in message.embeds
    ]
    parts += [
        f"[attachment] {attachment.filename} {attachment.url}"
        for attachment in message.attachments
    ]
    author = message.author.name if message.author else "Unknown"
    return f"{author} (message_id={message.id}): {' '.join(filter(None, parts)) or '[No content]'}"


async def list_guilds(arguments):
    if not client.is_ready():
        return reply("Discord connection is not ready yet. Please try again shortly.")
    return reply("\n".join(f"{guild.name} ({guild.id})" for guild in client.guilds))


async def list_channels(arguments):
    guild = client.get_guild(int(arguments["guild_id"]))
    if not guild:
        return reply("Guild not found")
    return reply(
        "\n".join(
            f"{channel.name} ({channel.id}) - {channel.type.name}"
            for channel in guild.channels
        )
    )


async def read_messages(arguments):
    channel_id = int(arguments["channel_id"])
    channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)
    if not isinstance(channel, discord.abc.Messageable):
        return reply("Cannot read messages from this channel.")
    limit = max(1, min(int(arguments.get("limit", 50)), 200))
    messages = [
        format_message(message) async for message in channel.history(limit=limit)
    ]
    return reply("\n".join(reversed(messages)))


async def search_messages(arguments):
    channel_id = int(arguments["channel_id"])
    channel = client.get_channel(channel_id) or await client.fetch_channel(channel_id)
    if not isinstance(channel, discord.abc.Messageable):
        return reply("Cannot read messages from this channel.")
    query = arguments["query"].lower()
    limit = max(1, min(int(arguments.get("limit", 50)), 200))
    messages = []
    async for message in channel.history(limit=min(limit * 2, limit + 100)):
        line = format_message(message)
        if query in line.lower():
            messages.append(line)
        if len(messages) == limit:
            break
    return reply(
        "\n".join(reversed(messages)) or f"No messages found matching '{query}'."
    )


TOOLS = [
    tool("list_guilds", "List guilds"),
    tool("list_channels", "List channels in a guild",
         {"guild_id": {"type": "string"}}, ["guild_id"]),
    tool("read_messages", "Read messages from a channel or thread",
         {"channel_id": {"type": "string"}, "limit": {"type": "integer"}},
         ["channel_id"]),
    tool("search_messages", "Search messages in a channel or thread",
         {"channel_id": {"type": "string"}, "query": {"type": "string"},
          "limit": {"type": "integer"}},
         ["channel_id", "query"]),
]
HANDLERS = {
    "list_guilds": list_guilds,
    "list_channels": list_channels,
    "read_messages": read_messages,
    "search_messages": search_messages,
}

client = discord.Client()
app = Server("discord-py-self-mcp")


@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name, arguments):
    handler = HANDLERS.get(name)
    if not handler:
        raise ValueError(f"Unknown tool '{name}'")
    try:
        return await handler(arguments)
    except Exception as error:
        return reply(f"Error: {error}")


async def run_app():
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        sys.stderr.write("Error: DISCORD_TOKEN is not set.\n")
        raise SystemExit(1)
    asyncio.create_task(client.start(token))
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    asyncio.run(run_app())


if __name__ == "__main__":
    main()

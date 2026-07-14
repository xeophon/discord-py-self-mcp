---
name: discord-py-self
description: Read-only access to Discord messages via a local selfbot MCP server using discord.py-self. Use when the user asks to read, list, or search Discord messages, channels, or guilds.
---

# Discord (discord.py-self MCP)

Read Discord messages through a local stdio MCP server backed by
[discord.py-self](https://github.com/dolfies/discord.py-self). The server
exposes four read-only tools: `list_guilds`, `list_channels`,
`read_messages`, and `search_messages`.

## Setup

Create a `.env` file with your Discord token:

```sh
cp .env.example .env
# edit .env and set your token
```

The skill loads `.env` automatically and launches the server
(`discord_py_self.server`) via the kernel Python.

## Usage

```python
import discord_py_self

# Discover available tools
for tool in await discord_py_self.list_tools():
    print(tool["name"], "-", tool["description"])

# List guilds / channels / messages
guilds = await discord_py_self.list_guilds()
channels = await discord_py_self.list_channels(guild_id="123456789")
messages = await discord_py_self.read_messages(channel_id="123456789", limit=50)
results = await discord_py_self.search_messages(channel_id="123456789", query="hello")
```

Notes:
- Every tool is an `async` method — always `await`.
- Results are plain text strings.
- The server must connect to Discord before tools are available; on first
  call it may take a few seconds to become ready.
- Discord prohibits automating user accounts — use a disposable account.

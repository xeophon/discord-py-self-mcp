# discord-py-self-mcp

Read-only Discord MCP server via
[`discord.py-self`](https://github.com/dolfies/discord.py-self).

Discord prohibits automating normal user accounts. Running this project can
result in account termination. Use a disposable account.

## Files

| Path | Description |
|---|---|
| `SKILL.md` | Skill frontmatter + docs |
| `.env.example` | Example environment file (copy to `.env`) |
| `pyproject.toml` | Package metadata, dependencies, console-script entry point |
| `src/discord_py_self/__init__.py` | `McpIntegration` subclass — binds the stdio server to the agent kernel |
| `src/discord_py_self/server.py` | MCP server logic (discord.py-self + MCP stdio) |

## Install

```sh
pip install .
cp .env.example .env  # then edit .env with your token
discord-py-self-mcp   # console-script entry point
```

Or as a module:

```sh
python -m discord_py_self.server
```

## Tools

| Tool | Args | Description |
|---|---|---|
| `list_guilds` | — | List guilds the account is in |
| `list_channels` | `guild_id` | List channels in a guild |
| `read_messages` | `channel_id`, `limit?` | Read recent messages |
| `search_messages` | `channel_id`, `query`, `limit?` | Search messages |

## License

MIT

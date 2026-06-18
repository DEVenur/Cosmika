---
description: "Write your own Discord slash commands and agent tools in Python, drop them into a gitignored custom/ directory, and let the agent call them — one function can be both a slash command and an LLM-callable tool."
tags:
  - Tools
  - Slash Commands
  - Custom code
  - Developers
---

# Custom Commands & Tools

Dango ships two ways to extend what the bot can do:

| Approach | Who it's for | Where |
|---|---|---|
| **No-code** — HTTP API & SQL tools configured as JSON / in the dashboard | Operators, non-developers | [Tools](tools.md#custom-api-tools) |
| **Code** — your own Python commands and agent tools | Developers | **this page** |

This page covers the **code** path: you write Python functions, drop them into a
`custom/` directory, and they become Discord slash commands, agent tools, or both.

## Git-safe by design

Everything you put in `custom/` (except the tracked templates and `README.md`) is
**gitignored**. Your code never shows up in `git status` and survives `git pull` —
no merge conflicts, no accidental commits of private logic or keys.

## Quick start

```bash
cp custom/commands.py.example custom/commands.py
cp custom/tools.py.example    custom/tools.py
# edit them, then restart the bot
```

Any `*.py` file in `custom/` is auto-loaded at startup. Use any filenames you like
and split your code across as many files as you want.

## The three decorators

```python
from dango.extensions import command, agent_tool, command_and_tool, Ctx
```

| Decorator | Discord slash command | Callable by the agent |
|---|:---:|:---:|
| `@command` | ✅ | ❌ |
| `@agent_tool` | ❌ | ✅ |
| `@command_and_tool` | ✅ | ✅ |

Whether the agent can call your function is decided **only** by the decorator —
there is no global switch, so exposing a function to the LLM is always an explicit,
per-function opt-in. Keep destructive or privileged actions on `@command`.

## A command the agent can also call

```python
from dango.extensions import command_and_tool, Ctx

@command_and_tool(name="stock", description="Get a stock quote by ticker")
async def stock(ctx: Ctx, ticker: str) -> str:
    """Look up the latest price for a stock ticker.

    Args:
        ticker: The stock symbol, e.g. AAPL.
    """
    data = await fetch_quote(ticker)
    return f"{ticker}: ${data['price']} ({data['pct']}%)"
```

That single function gives you:

- a `/stock ticker:AAPL` slash command in Discord, and
- a `stock` tool the model can call on its own when a user asks *"how's Apple doing?"*

## Writing a function

- **Return a string.** As a command it is sent as the reply; as a tool it is
  returned to the model. Return `None` and a command just acknowledges with ✅.
- **`ctx` is optional.** Declare `ctx: Ctx` as the **first** parameter to receive
  call context. Omit it if you don't need it.
- **Use scalar parameters for `@command_and_tool`** (`str`, `int`, `bool`,
  `float`) so both the Discord command schema and the agent tool schema can
  represent them. `@command`-only functions may use richer Discord types
  (`discord.Member`, `discord.Attachment`, …).
- **Write a docstring with an `Args:` section.** The agent reads it to decide when
  and how to call your tool, so be descriptive.
- **`async def` and `def` are both supported.**

## The `Ctx` object

`ctx` normalizes the two call paths so one function body works for both.

| Attribute | Type | Notes |
|---|---|---|
| `ctx.source` | `str` | `"discord_command"` or `"agent"` |
| `ctx.author_name` | `str` | Display name of the user |
| `ctx.author_id` | `int \| None` | Set on the command path |
| `ctx.channel_id` | `int \| None` | |
| `ctx.channel_name` | `str` | |
| `ctx.guild_id` | `int \| None` | |
| `ctx.guild_name` | `str` | |
| `ctx.interaction` | `discord.Interaction \| None` | Only on the command path |
| `ctx.bot` | `commands.Bot \| None` | Only on the command path |

Branch on `ctx.source` when a function needs to behave differently depending on
who called it:

```python
@command_and_tool(name="whoami")
def whoami(ctx: Ctx) -> str:
    if ctx.source == "discord_command":
        return f"You ran /whoami in #{ctx.channel_name}."
    return f"{ctx.author_name} is asking via chat."
```

## How loading works

- On startup the bot imports every `custom/*.py` once (`*.example` files are
  skipped), then registers tools on the agent and slash commands on the bot.
- A **missing `custom/` directory** or a **broken file** is logged and skipped —
  it never crashes the bot. Look for `🧩 [custom]` / `⚠️ [custom]` lines in the log.
- New slash commands are synced to Discord on the next startup (during `on_ready`).
  Restart the bot after adding or changing a command.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `CUSTOM_DIR` | `custom` | Directory scanned for `*.py` extension files |

See also: [Tools](tools.md) for the no-code HTTP API and SQL tools, and
[Slash Commands](../usage/commands.md) for the built-in commands.

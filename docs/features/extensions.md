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
| `ctx.author_id` | `int \| None` | The caller's Discord user ID |
| `ctx.channel_id` | `int \| None` | |
| `ctx.channel_name` | `str` | |
| `ctx.guild_id` | `int \| None` | |
| `ctx.guild_name` | `str` | |
| `ctx.mentioned_user_ids` | `list[int]` | IDs of members the message tagged. Agent path only — empty for slash commands |
| `ctx.mentioned_role_ids` | `list[int]` | IDs of roles the message tagged. Agent path only — empty for slash commands |
| `ctx.author_permissions` | `list[str]` | Permission names the caller holds in the guild (e.g. `"manage_guild"`). Empty in DMs |
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

### Mentions and permissions

When a user @-mentions members or roles in a chat message, the framework hands
your tool the **exact IDs** — no need to fuzzy-match display names against the
guild's member or role list. Because Discord mention syntax is built straight
from the ID (`<@user_id>`, `<@&role_id>`), a tool can echo a real, clickable
ping back into the channel using only what's on `ctx`:

```python
@agent_tool(name="page_role")
def page_role(ctx: Ctx) -> str:
    # "page @Moderator about this"  →  precise role IDs, already resolved.
    if not ctx.mentioned_role_ids:
        return "Tag a role to page."
    mentions = " ".join(f"<@&{rid}>" for rid in ctx.mentioned_role_ids)
    return f"Paging {mentions} 🍡"
```

`ctx.author_permissions` lets a tool gate privileged actions on the caller's
own Discord permissions before doing anything:

```python
    if "manage_guild" not in ctx.author_permissions:
        return "You need Manage Server to do that."
```

!!! note "Mention/permission fields and the agent path"
    `mentioned_user_ids` and `mentioned_role_ids` come from the triggering chat
    message, so they populate on the **agent path** and are empty for slash
    commands (which carry no message mentions). `author_permissions` is
    populated on **both** paths but is empty in DMs, where there is no guild to
    grant permissions.

!!! warning "Acting on the IDs needs a Discord client"
    The IDs identify who was tagged, but mutating Discord state (adding roles,
    fetching members) needs a `discord.py` client. `ctx.bot` is set **only on
    the command path** — on the agent path it is `None`. So agent-path tools can
    *reference* mentioned users/roles (build mention strings, gate on
    permissions, return them for the model to reason about) but cannot perform
    member/role mutations directly.

## Using built-in Agno toolkits & context providers

Beyond writing your own functions, you can attach any
[Agno toolkit](https://docs.agno.com/tools/toolkits) or
[context provider](https://docs.agno.com/context-providers) to the agent from a
custom file with `register_tools()` — no core code changes:

```python
from dango.extensions import register_tools
from agno.context.gdrive import GoogleDriveContextProvider

# A context provider exposes its tools via get_tools()
register_tools(*GoogleDriveContextProvider(corpora="user").get_tools())
```

`register_tools()` accepts plain functions, `@tool` functions, `Toolkit`
instances, or lists (such as a provider's `get_tools()`). Everything you pass is
exposed to the **agent only** — it never becomes a Discord slash command. This is
the same mechanism Dango uses internally for its SQL database tools.

Agno ships context providers for Google Drive, Gmail, Calendar, Slack, web, wiki,
the filesystem, and more. Some need extra packages and credentials — e.g. Drive
needs `google-api-python-client google-auth-httplib2 google-auth-oauthlib` plus
OAuth. Install those in your clone the usual way (`uv add ...`).

!!! note "Agno's Scheduler does not apply"
    Agno's [Scheduler](https://docs.agno.com/scheduler/overview) is a runtime/cron
    orchestration layer that drives AgentOS endpoints — it is not a tool and does
    not plug into Dango's discord.py + Workflow model. For scheduled behaviour,
    use `discord.ext.tasks` or an external cron job.

## Interactive UI (modals, buttons, selects) — not supported here

This SDK is built around a simple contract: **your function takes arguments and
returns a string, and the framework sends it.** Under the hood the command path
calls `interaction.response.defer()` and then `followup.send(...)` for you. That
contract has two consequences:

- **No Discord UI components.** You cannot pop up a modal or attach buttons /
  select menus from an extension function — a modal must be the *first* response
  to an interaction, but the framework has already deferred it. This applies to
  `@command` too, not just the agent path.
- **The agent path has no interaction.** When the LLM calls your function,
  `ctx.interaction` is `None` and there is no human in the loop to fill a form.

**How the agent "fills in" missing input:** it asks. If a tool needs more
information the model simply asks a follow-up question in chat ("Which ticker?"),
the user replies, and the agent calls the tool again with the answer. Collection
is conversational, not a popup.

**If you genuinely need a modal / button flow,** write a normal `discord.py`
command or Cog directly (outside this SDK) so you own the interaction lifecycle.
To also let the agent do the same job, add a separate `@agent_tool` whose
parameters are the fields the modal would collect, and have both call one shared
logic function:

```python
async def _create_event(title: str, when: str) -> str:
    ...  # shared core logic

@agent_tool(description="Create a calendar event")
async def create_event(title: str, when: str) -> str:
    """Args: title: event title. when: ISO datetime."""
    return await _create_event(title, when)

# The modal-based version lives in your own discord.py Cog and also calls _create_event().
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

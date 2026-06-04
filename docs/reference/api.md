# API Reference

All public symbols are re-exported from the `dango` top-level package. You can import everything from `dango` directly — you never need to reach into sub-modules.

## Quick import table

```python
from dango import (
    # Cogs
    ChatCog,
    AdminCog,

    # Workflow
    create_discord_workflow,

    # Config
    RuntimeConfig,

    # Tool decorator & context
    discord_tool,
    RunContext,
    ContextMenuDef,

    # Context accessors
    get_discord_context,
    get_discord_bot,
    get_discord_interaction,

    # Response helpers
    set_ephemeral,
    set_discord_response,

    # Permission helpers
    check_roles,
    check_permissions,
)
```

## Where things live

| Symbol | Top-level import | Sub-module (also works) |
|---|---|---|
| `ChatCog` | `from dango import ChatCog` | `from dango.commands import ChatCog` |
| `AdminCog` | `from dango import AdminCog` | `from dango.commands import AdminCog` |
| `create_discord_workflow` | `from dango import create_discord_workflow` | `from dango.workflow import create_discord_workflow` |
| `RuntimeConfig` | `from dango import RuntimeConfig` | `from dango.utils.runtime_config import RuntimeConfig` |
| `discord_tool` | `from dango import discord_tool` | `from dango.tools import discord_tool` |
| `RunContext` | `from dango import RunContext` | `from dango.tools import RunContext` |
| `ContextMenuDef` | `from dango import ContextMenuDef` | `from dango.tools import ContextMenuDef` |
| `get_discord_context` | `from dango import get_discord_context` | `from dango.tools import get_discord_context` |
| `get_discord_bot` | `from dango import get_discord_bot` | `from dango.tools import get_discord_bot` |
| `get_discord_interaction` | `from dango import get_discord_interaction` | `from dango.tools import get_discord_interaction` |
| `set_ephemeral` | `from dango import set_ephemeral` | `from dango.tools import set_ephemeral` |
| `set_discord_response` | `from dango import set_discord_response` | `from dango.tools import set_discord_response` |
| `check_roles` | `from dango import check_roles` | `from dango.tools import check_roles` |
| `check_permissions` | `from dango import check_permissions` | `from dango.tools import check_permissions` |

## Symbol reference

### `ChatCog`

Discord.py Cog that handles incoming messages and interactions. Wraps the Agno workflow and routes Discord events into the four-step pipeline.

**Constructor:**

```python
ChatCog(
    bot: commands.Bot,
    discord_workflow: Workflow,
    chat_system_prompt: str,
    runtime_config: RuntimeConfig,
    extra_tools: list | None = None,
    context_menu_defs: list[ContextMenuDef] | None = None,
)
```

### `AdminCog`

Discord.py Cog that registers admin slash commands (`/addchannel`, `/adduser`, etc.). Requires the **Administrator** server permission for all commands.

**Constructor:**

```python
AdminCog(bot: commands.Bot, runtime_config: RuntimeConfig)
```

### `create_discord_workflow()`

Creates and returns the Agno `Workflow` object. Call once at startup; pass the result to `ChatCog`.

### `RuntimeConfig(config_path)`

Loads and manages `config/runtime.yml`. Stores allowed channels, allowed DM users, history limit, timezone, and activity string. Pass the same instance to both `ChatCog` and `AdminCog`.

### `discord_tool`

Decorator that wraps an async or sync function as an Agno tool. See [Embedding — Wrapping commands as tools](../advanced/embedding.md#wrapping-commands-as-tools) for the full rules.

### `RunContext`

Type alias for the Agno `RunContext`. Add it as the last parameter of any `@discord_tool` function — Agno injects it automatically and it is not exposed to the LLM.

### `ContextMenuDef`

Dataclass for registering right-click context menu commands. See [Embedding — Context menu commands](../advanced/embedding.md#context-menu-commands).

### Context accessors

| Function | Returns |
|---|---|
| `get_discord_context(run_context)` | `dict` with `author_id`, `author_name`, `author_roles`, `channel_id`, `channel_name`, `guild_id`, `guild_name` |
| `get_discord_bot(run_context)` | `discord.Client` — the bot instance |
| `get_discord_interaction(run_context)` | `discord.Interaction \| None` — present for button/modal/context-menu requests, `None` for regular messages |

### Response helpers

| Function | Effect |
|---|---|
| `set_ephemeral(run_context)` | Makes the response visible only to the invoking user (Interactions only) |
| `set_discord_response(run_context, embeds=None, suppress_text=False)` | Attach `discord.Embed` objects and/or suppress the LLM text output |

### Permission helpers

| Function | Returns |
|---|---|
| `check_roles(run_context, any_of=None, all_of=None)` | Error string if check fails, `None` if it passes |
| `check_permissions(run_context, any_of=None, all_of=None)` | Error string if check fails, `None` if it passes |

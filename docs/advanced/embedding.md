---
description: "Embed Dango's AI agent into any existing discord.py bot. Drop in ChatCog and AdminCog to add natural-language chat, web search, and workspace access without touching your existing slash commands."
tags:
  - Advanced
  - Embedding
  - discord.py
  - Developers
---

# Embedding into Another Bot

Dango's agent lives in a standard discord.py Cog, so you can drop it into any existing bot. The bot keeps all its slash commands and prefix commands; Dango adds these capabilities on top:

| Feature | Env var | What it does |
|---|---|---|
| **Chat** | (always on) | Natural-language conversation with automatic history context |
| **Web search** | `ENABLE_DUCKDUCKGO=on` | Agent searches the web when it needs up-to-date information |
| **Read URL** | `ENABLE_WEBSITE_TOOLS=on` | Agent reads linked pages that appear in messages |
| **Workspace** | `ENABLE_WORKSPACE=on` | Agent reads files from a local directory (read-only) |

All features are opt-in via environment variables — no code changes required beyond loading the Cogs once.

---

## Chat

The agent reads conversation history automatically and replies in context. The only required configuration is an LLM provider:

```env
FAST_MODEL=google:gemini-2.0-flash
FAST_API_KEY=your_api_key_here
```

**Channel mode vs mention mode**

By default the bot only responds when directly @mentioned. To make it respond to every message in specific channels, configure allowed channels one of two ways:

- **Programmatic** — pass `default_channels` to `RuntimeConfig` if you know the channel IDs upfront. These are seeded into `config/runtime.yml` on the very first run; subsequent starts use whatever is in the YAML, so admin `/removechannel` changes are preserved:

  ```python
  runtime_config = RuntimeConfig("config/runtime.yml", default_channels=[YOUR_CHANNEL_ID])
  ```

- **Runtime** — let a Discord admin run `/addchannel` in each target channel after the bot is running.

Channel configuration is stored in `config/runtime.yml` (auto-created on first run). Without any allowed channels the bot still works, but users must @mention it every time.

---

## Web search

Set `ENABLE_DUCKDUCKGO=on` to let the agent search the web when it needs up-to-date information:

```env
ENABLE_DUCKDUCKGO=on
```

No API key needed. The agent decides on its own when to search — users don't have to ask explicitly.

---

## Read URL

Set `ENABLE_WEBSITE_TOOLS=on` to let the agent fetch and read the content of URLs that appear in messages:

```env
ENABLE_WEBSITE_TOOLS=on
```

---

## Workspace

The Workspace tool gives the agent read-only access to a local directory. Useful for bots that want the agent to answer questions about documentation, logs, or any files on the host machine.

```env
ENABLE_WORKSPACE=on
WORKSPACE_ROOT=workspace   # optional — defaults to ./workspace relative to the bot's working directory
```

The agent can **read**, **list**, and **search** files inside `WORKSPACE_ROOT`. Write access is intentionally disabled.

!!! warning "Workspace init is not automatic when embedding"
    When running Dango as a standalone bot (`main.py`), workspace context is initialised automatically. When embedding Dango as a package, you must call `workspace_context.init()` yourself in `setup_hook` — otherwise the workspace system prompt is never generated and the agent has no knowledge of the workspace files.

    ```python
    import os
    from dango.utils import workspace_context

    @bot.event
    async def setup_hook():
        if os.getenv("ENABLE_WORKSPACE") == "on":
            await workspace_context.init(
                os.getenv("WORKSPACE_ROOT", "workspace"),
                os.getenv("WORKSPACE_SYS_PROMPT_PATH", "config/workspace_sys_prompt.txt"),
            )
        # ... add_cog calls below
    ```

    `workspace_context.init()` reads the workspace files, generates a topic-index system prompt block, and caches it. The cache is invalidated automatically whenever workspace files change.

---

## Installation

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install git+https://github.com/zhiro-labs/dango
```

## Loading the Cogs

Dango reads environment variables at **import time**, so `load_dotenv()` must be called before any `dango` import. Place it at the very top of your entry-point file:

```python
# main.py — top of file, before all other imports
from dotenv import load_dotenv
load_dotenv()

# Only import dango after env vars are loaded
import discord
from discord.ext import commands
from dango import ChatCog, AdminCog, create_discord_workflow, RuntimeConfig
from dango.utils import workspace_context
```

Then load the Cogs in `setup_hook`:

```python
@bot.event
async def setup_hook():
    import os

    # Workspace init (only if ENABLE_WORKSPACE=on)
    if os.getenv("ENABLE_WORKSPACE") == "on":
        await workspace_context.init(
            os.getenv("WORKSPACE_ROOT", "workspace"),
            os.getenv("WORKSPACE_SYS_PROMPT_PATH", "config/workspace_sys_prompt.txt"),
        )

    with open(os.getenv("CHAT_SYS_PROMPT_PATH", "config/chat_sys_prompt.txt"), encoding="utf-8") as f:
        chat_system_prompt = f.read()

    runtime_config = RuntimeConfig("config/runtime.yml")
    discord_workflow = create_discord_workflow()

    await bot.add_cog(ChatCog(bot, discord_workflow, chat_system_prompt, runtime_config))
    await bot.add_cog(AdminCog(bot, runtime_config))
```

!!! warning "Do not use `on_ready` for Cog registration"
    Always add Cogs inside `setup_hook`, not `on_ready`. The `setup_hook` event runs once before the bot connects and guarantees Cogs are registered before any events are dispatched. Using `on_ready` can miss events that fire during connection.

**`create_discord_workflow()`** returns the Agno `Workflow` that wires together the four pipeline steps (fetch history → call agent → render tables → send response). Call it once at startup and pass the result to `ChatCog`.

**`RuntimeConfig(config_path, default_channels=None)`** loads `config/runtime.yml` (created automatically on first run). It stores the allowed channel and user lists, timezone, history limit, and activity string. Pass the same instance to both `ChatCog` and `AdminCog` so admin commands take effect immediately. `default_channels` pre-seeds the channel list when no YAML exists yet — ignored on subsequent starts so `/removechannel` changes are preserved.

**`AdminCog`** adds the following slash commands (all require the **Administrator** server permission, all responses are ephemeral):

| Command | Description |
|---|---|
| `/addchannel` | Allow the bot to respond to all messages in the current channel |
| `/removechannel` | Remove the current channel from the allowed list |
| `/listchannels` | Show all allowed channels |
| `/adduser @user` | Allow a user to DM the bot |
| `/removeuser @user` | Remove a user from the DM allowlist |
| `/listusers` | Show all allowed DM users |
| `/sethistorylimit <n>` | Number of past messages to include as context |
| `/settimezone <tz>` | Timezone for timestamps in the system prompt |
| `/setactivity <text>` | Bot's Discord activity status |
| `/refreshmetadata` | Refresh stored display names for channels and users |

## `ChatCog` parameters

| Parameter | Type | Description |
|---|---|---|
| `bot` | `commands.Bot` | Your bot instance |
| `discord_workflow` | `Workflow` | Created by `create_discord_workflow()` |
| `chat_system_prompt` | `str` | System prompt for the agent |
| `runtime_config` | `RuntimeConfig` | Allowed channels, users, history limit, timezone |

---

## Full example — Neko reminder bot

Neko is a Discord bot with slash commands for event management: `/event`, `/event-list`, `/event-delete`, `/set-reminder-timezone`, and `/set-reminder-channel`. This walkthrough adds Dango so users can chat naturally with the bot — while every existing slash command keeps working unchanged.

### Step 1 — Install Dango

Run this in the Neko project directory:

```bash
uv add git+https://github.com/zhiro-labs/dango
```

### Step 2 — Configure `.env`

Add to Neko's `.env`:

```env
# LLM provider
FAST_MODEL=google:gemini-2.0-flash
FAST_API_KEY=your_api_key_here

# System prompt path
CHAT_SYS_PROMPT_PATH=config/chat_sys_prompt.txt

# Optional built-in tools
ENABLE_DUCKDUCKGO=on
ENABLE_WEBSITE_TOOLS=on
```

### Step 3 — Create the system prompt

Create `config/chat_sys_prompt.txt`. Describe the bot's persona and what Neko's existing slash commands do, so the agent can guide users to the right command:

```
You are Neko, a Discord event reminder assistant.

You can help users with questions and provide guidance on:
- Creating events: use the /event command
- Viewing upcoming events: use the /event-list command
- Deleting events: use the /event-delete command
- Setting the reminder timezone: use /set-reminder-timezone
- Setting the reminder channel: use /set-reminder-channel

Reply in a friendly and helpful tone.
```

### Step 4 — Update `main.py`

`load_dotenv()` must come **before** any dango import. Add the Dango integration inside `setup_hook`:

```python
# main.py — top of file
from dotenv import load_dotenv
load_dotenv()  # MUST be before dango imports

import os
import discord
from discord.ext import commands
from dango import ChatCog, AdminCog, create_discord_workflow, RuntimeConfig

# ... rest of Neko's existing imports ...

bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents(
        guilds=True,
        guild_messages=True,
        message_content=True,    # required for ChatCog to read messages
        members=True,            # required for member display names
        dm_messages=True,
    ),
)

@bot.event
async def setup_hook():
    # ... Neko's existing setup (db.init_db(), etc.) ...

    with open(os.getenv("CHAT_SYS_PROMPT_PATH", "config/chat_sys_prompt.txt"), encoding="utf-8") as f:
        chat_system_prompt = f.read()

    runtime_config = RuntimeConfig("config/runtime.yml", default_channels=[YOUR_CHANNEL_ID])
    discord_workflow = create_discord_workflow()

    await bot.add_cog(ChatCog(bot, discord_workflow, chat_system_prompt, runtime_config))
    await bot.add_cog(AdminCog(bot, runtime_config))

    await bot.tree.sync()
```

Replace `YOUR_CHANNEL_ID` with the integer ID of the channel where you want Neko to respond to all messages. Administrators can also use `/addchannel` at runtime.

### Step 5 — Add runtime files to `.gitignore`

These files are auto-generated and should not be committed:

```
config/runtime.yml
config/workspace_sys_prompt.txt
config/workspace_sys_prompt.fingerprint.json
```

### Result

All original slash commands keep working unchanged. Users can now also chat with Neko in plain English — the agent answers questions, provides guidance on which commands to use, and can search the web if `ENABLE_DUCKDUCKGO=on` is set.

Admin commands from `AdminCog` are also available: `/addchannel`, `/removechannel`, `/settimezone`, `/sethistorylimit`, etc.

---

## Updating

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install --upgrade git+https://github.com/zhiro-labs/dango
```

Restart your bot to pick up the new version.

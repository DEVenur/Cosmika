# Embedding into Another Bot

Dango's agent lives in a standard discord.py Cog, so you can drop it into any existing bot. The bot keeps all its slash commands and prefix commands; Dango adds a natural-language layer on top.

## Installation

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install git+https://github.com/zhiro-labs/dango
```

## Loading the Cogs

Set the required environment variables before importing (e.g. via `load_dotenv()`), then load the Cogs in `setup_hook`:

```python
from dango import ChatCog, AdminCog, create_discord_workflow, RuntimeConfig

with open("config/chat_sys_prompt.txt", encoding="utf-8") as f:
    chat_system_prompt = f.read()

runtime_config = RuntimeConfig("config/runtime.yml")
discord_workflow = create_discord_workflow()

await bot.add_cog(ChatCog(bot, discord_workflow, chat_system_prompt, runtime_config))
await bot.add_cog(AdminCog(bot, runtime_config))
```

**`create_discord_workflow()`** returns the Agno `Workflow` that wires together the four pipeline steps (fetch history → call agent → render tables → send response). Call it once at startup and pass the result to `ChatCog`.

**`RuntimeConfig(config_path)`** loads `config/runtime.yml` (created automatically on first write). It stores the allowed channel and user lists, timezone, history limit, and activity string. Pass the same instance to both `ChatCog` and `AdminCog` so admin commands take effect immediately.

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
| `extra_tools` | `list \| None` | `@discord_tool`-wrapped functions the agent can call |
| `context_menu_defs` | `list[ContextMenuDef] \| None` | Right-click context menu commands |

---

## Wrapping commands as tools

The agent can call your existing bot commands as tools. Users can ask naturally ("ban spammer") and the agent decides when to invoke `ban_user` — without breaking the original `!ban` or `/ban` commands.

### 1. Extract the logic and wrap it

```python
from dango.tools import discord_tool, RunContext, get_discord_context

@discord_tool(name="play_music")
async def play_music(song: str, run_context: RunContext) -> str:
    """Play music in the voice channel.

    Args:
        song (str): Song name or YouTube/Spotify URL
    """
    ctx = get_discord_context(run_context)
    if ctx["guild_id"] is None:
        return "This command can only be used in a server channel."
    await music_player.play(ctx["guild_id"], song)
    return f"Now playing: {song}"
```

### 2. Pass tools to `ChatCog`

```python
await bot.add_cog(ChatCog(
    bot, workflow, chat_system_prompt, runtime_config,
    extra_tools=[play_music],
))
```

Your original `!play` / `/play` commands keep working unchanged.

### Tool function rules

| Rule | Detail |
|---|---|
| Type hints | Required on every parameter and return value |
| Docstring | First line = tool description shown to the LLM |
| `Args:` block | One line per parameter; Agno parses this for the tool schema |
| `run_context: RunContext` | Agno injects this automatically — not exposed to the LLM |
| Return value | `str` by default; can be `""` when using `set_discord_response()` |
| Async or sync | Both work |

---

## Context helpers

### `get_discord_context(run_context)`

Returns the Discord request context as a dict:

```python
from dango.tools import discord_tool, RunContext, get_discord_context

@discord_tool(name="my_tool")
async def my_tool(run_context: RunContext) -> str:
    ctx = get_discord_context(run_context)
    # ctx["author_id"]          — int | None
    # ctx["author_name"]        — str
    # ctx["author_roles"]       — list[str]  (guild role names, excludes @everyone)
    # ctx["channel_id"]         — int | None
    # ctx["channel_name"]       — str
    # ctx["guild_id"]           — int | None  (None in DMs)
    # ctx["guild_name"]         — str
    ...
```

### `get_discord_bot(run_context)`

Returns the `discord.Bot` instance. Use this when a tool needs to send messages, fetch channels, or trigger native Discord UI:

```python
from dango.tools import get_discord_bot

bot = get_discord_bot(run_context)
channel = bot.get_channel(ctx["channel_id"])
await channel.send("Hello from a tool!")
```

### `get_discord_interaction(run_context)`

Returns the `discord.Interaction` that triggered this request, or `None` for regular chat messages. Present for button clicks, select menus, modal submits, and context menus.

---

## Permission helpers

### `check_roles()` — custom role names

```python
from dango.tools import check_roles

@discord_tool(name="ban_user")
async def ban_user(username: str, reason: str, run_context: RunContext) -> str:
    """Ban a user. Requires Moderator or Admin role.

    Args:
        username (str): Display name of the user to ban
        reason (str): Reason for the ban
    """
    if err := check_roles(run_context, any_of=["Moderator", "Admin"]):
        return err
    # ... logic ...
```

| Parameter | Description |
|---|---|
| `any_of` | User must have **at least one** of these role names |
| `all_of` | User must have **every** one of these role names |

Returns an error string if the check fails, `None` if it passes.

### `check_permissions()` — Discord built-in permissions

For Discord's built-in permissions (`manage_guild`, `ban_members`, etc.) rather than custom role names:

```python
from dango.tools import check_permissions

@discord_tool(name="set_timezone")
async def set_timezone(timezone: str, run_context: RunContext) -> str:
    """Set the server's reminder timezone.

    Args:
        timezone (str): Timezone name, e.g. Asia/Taipei
    """
    if err := check_permissions(run_context, any_of=["manage_guild"]):
        return err
    # ... logic ...
```

Common permission names: `administrator`, `manage_guild`, `manage_roles`, `manage_channels`, `ban_members`, `kick_members`, `manage_messages`, `moderate_members`.

---

## Response helpers

### `set_ephemeral()` — private response

Makes the response visible only to the invoking user. Only effective when the request came from a Discord Interaction (slash command, button, modal, context menu) — has no effect on regular chat messages.

```python
from dango.tools import set_ephemeral

@discord_tool(name="get_balance")
async def get_balance(run_context: RunContext) -> str:
    """Check your personal balance. Response is private."""
    set_ephemeral(run_context)
    return f"Your balance: 1000 coins"
```

### `set_discord_response()` — embed output and text suppression

Attach `discord.Embed` objects to the response, or suppress the LLM's text output entirely:

```python
import discord
from dango.tools import set_discord_response

@discord_tool(name="list_events")
async def list_events(run_context: RunContext) -> str:
    """List upcoming events."""
    embed = discord.Embed(title="Upcoming Events", color=discord.Color.blurple())
    embed.add_field(name="Concert", value="Saturday 19:00", inline=False)

    set_discord_response(run_context, embeds=[embed], suppress_text=True)
    set_ephemeral(run_context)
    return ""  # text is suppressed; only the embed is sent
```

| Parameter | Description |
|---|---|
| `embeds` | List of `discord.Embed` objects (max 10 per message) |
| `suppress_text` | If `True`, the LLM's generated text is not sent — only embeds and table images |

---

## Native Discord UI (stateful multi-step forms)

For complex interactive UI — multi-select dropdowns, confirm buttons, multi-step forms — use `discord.ui.View` directly. The `View` manages its own state through Python callbacks; no Dango routing needed.

```python
from dango.tools import discord_tool, RunContext, get_discord_bot, get_discord_context, set_discord_response

@discord_tool(name="open_event_form")
async def open_event_form(title: str, run_context: RunContext) -> str:
    """Open an interactive form to configure a new event.

    Args:
        title (str): Event title
    """
    bot = get_discord_bot(run_context)
    ctx = get_discord_context(run_context)
    channel = bot.get_channel(ctx["channel_id"])

    # EventView is a standard discord.ui.View — it manages role/reminder
    # selection state internally through Python callbacks.
    view = EventView(title=title, ...)
    await channel.send(f"Configure **{title}**:", view=view)

    set_discord_response(run_context, suppress_text=True)
    return ""
```

The key difference from `dango_component:` routing: `EventView`'s buttons and selects call their Python callbacks directly — the LLM is not involved after the form appears. Use this pattern when the UI has complex local state (e.g. three selects whose values must all be read together on confirm).

---

## `on_interaction` routing (modal & component)

For simpler interactions where you *do* want the LLM to process the result, prefix `custom_id` with `dango_modal:` or `dango_component:`. Dango routes these back through the full workflow automatically.

!!! warning "`custom_id` length limit"
    Discord enforces a 100-character limit on `custom_id`. The prefixes themselves consume some of that space:

    | Prefix | Prefix length | Remaining for your ID |
    |---|---|---|
    | `dango_component:` | 17 chars | 83 chars |
    | `dango_modal:` | 12 chars | 88 chars |

    IDs that exceed the limit are silently truncated by Discord, which will break routing.

### Modal submit

```python
import discord

# Slash command opens the modal — no deferring, no workflow run here.
@bot.tree.command(name="report")
async def report_command(interaction: discord.Interaction):
    modal = discord.ui.Modal(title="Submit Report", custom_id="dango_modal:report")
    modal.add_item(discord.ui.TextInput(label="Issue", custom_id="issue"))
    modal.add_item(discord.ui.TextInput(label="Details", custom_id="details",
                                         style=discord.TextStyle.paragraph))
    await interaction.response.send_modal(modal)

# When submitted, on_interaction sees the dango_modal: prefix and routes
# through the workflow. The LLM receives:
#   [Modal submitted: report]
#   issue: Can't send messages
#   details: Getting a permission error since yesterday
```

The LLM then decides which tool to call based on the form contents.

### Button / select click

```python
import discord

# Tool sends a message with a dango_component:-prefixed button.
@discord_tool(name="confirm_delete")
async def confirm_delete(channel_name: str, run_context: RunContext) -> str:
    """Ask for confirmation before deleting a channel.

    Args:
        channel_name (str): Channel to delete
    """
    bot = get_discord_bot(run_context)
    ctx = get_discord_context(run_context)
    channel = bot.get_channel(ctx["channel_id"])

    view = discord.ui.View()
    view.add_item(discord.ui.Button(
        label="Confirm delete",
        style=discord.ButtonStyle.danger,
        custom_id=f"dango_component:delete_confirmed:{channel_name}",
    ))
    view.add_item(discord.ui.Button(
        label="Cancel",
        style=discord.ButtonStyle.secondary,
        custom_id="dango_component:delete_cancelled",
    ))
    await channel.send(f"Delete **#{channel_name}**?", view=view)
    set_discord_response(run_context, suppress_text=True)
    return ""

# When a button is clicked, the LLM receives:
#   [Button: delete_confirmed:general]
#   Context: Delete **#general**?
# and can call the actual delete tool.
```

---

## Context menu commands

Register right-click commands that route through the agent:

```python
from dango import ChatCog, ContextMenuDef, create_discord_workflow

workflow = create_discord_workflow()

await bot.add_cog(ChatCog(
    bot,
    workflow,
    chat_system_prompt,
    runtime_config,
    context_menu_defs=[
        # Right-click a message → "Translate"
        ContextMenuDef(
            name="Translate",
            target="message",
            content_builder=lambda text: f"Translate this message to English:\n{text}",
        ),
        # Right-click a user → "User Info"
        ContextMenuDef(name="User Info", target="user"),
    ],
))
```

| `ContextMenuDef` field | Description |
|---|---|
| `name` | Label shown in Discord's right-click menu (max 32 chars) |
| `target` | `"message"` or `"user"` |
| `content_builder` | Optional callable `(str) → str`; transforms the target text into the agent's input. Defaults to `[Context menu: <name>]\nTarget: <text>` |

The `str` argument passed to `content_builder` depends on `target`:

| `target` | `str` value |
|---|---|
| `"message"` | The message's text content (`message.content`) |
| `"user"` | The user's display name — **not** the user ID or mention string |

---

## Full example — Neko reminder bot

Neko is a Discord bot with slash commands for event management: `/event`, `/event-list`, `/event-delete`, `/set-reminder-timezone`, and `/set-reminder-channel`. This walkthrough adds Dango so users can invoke the same functionality through natural language — while every existing slash command keeps working unchanged.

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
```

### Step 3 — Create the system prompt

Create `config/chat_sys_prompt.txt`:

```
You are Neko, a Discord event reminder assistant.
You can help users create events, list upcoming events, delete events,
and configure the reminder timezone and channel.
```

### Step 4 — Create `neko_tools.py`

This file wraps each command's logic as an Agno tool. Neko's original slash commands are not touched.

```python
# neko_tools.py
import discord
from dango import (
    RunContext, discord_tool,
    get_discord_context, get_discord_bot,
    check_permissions, set_ephemeral, set_discord_response,
)
import db
# NOTE: main.py imports neko_tools at the top level, so we cannot import from
# main at module level here — that would create a circular import.
# Import helpers lazily, inside each function that needs them.


@discord_tool(name="set_reminder_timezone")
async def set_reminder_timezone(timezone: str, run_context: RunContext) -> str:
    """Set the server's reminder timezone.

    Args:
        timezone (str): Timezone name, e.g. Asia/Taipei
    """
    if err := check_permissions(run_context, any_of=["manage_guild"]):
        return err
    ctx = get_discord_context(run_context)
    db.set_timezone(ctx["guild_id"], timezone)
    set_ephemeral(run_context)
    return f"Server timezone set to `{timezone}`."


@discord_tool(name="set_reminder_channel")
async def set_reminder_channel(run_context: RunContext) -> str:
    """Set the current channel as the reminder channel."""
    if err := check_permissions(run_context, any_of=["manage_guild"]):
        return err
    ctx = get_discord_context(run_context)
    db.set_reminder_channel(ctx["guild_id"], ctx["channel_id"])
    set_ephemeral(run_context)
    return f"Reminder channel set to <#{ctx['channel_id']}>."


@discord_tool(name="list_events")
async def list_events(run_context: RunContext) -> str:
    """List all upcoming events."""
    from main import discord_ts  # deferred to avoid circular import
    ctx = get_discord_context(run_context)
    bot = get_discord_bot(run_context)
    reminder_channel_id = db.get_reminder_channel(ctx["guild_id"])
    if not reminder_channel_id:
        return "⚠️ No reminder channel configured. Use `/set-reminder-channel` first."

    events = db.get_upcoming_events(reminder_channel_id)
    if not events:
        return "No upcoming events."

    guild = bot.get_guild(ctx["guild_id"])
    embed = discord.Embed(title="Upcoming Events", color=discord.Color.blurple())
    for event in events:
        roles = [guild.get_role(rid) for rid in event.role_ids]
        users = [guild.get_member(uid) for uid in event.user_ids]
        mentions = " ".join([r.mention for r in roles if r] + [u.mention for u in users if u])
        value = f"📅 {discord_ts(event.event_time, 'F')}"
        if mentions:
            value += f"\n👥 {mentions}"
        embed.add_field(name=event.title, value=value, inline=False)

    set_ephemeral(run_context)
    set_discord_response(run_context, embeds=[embed], suppress_text=True)
    return ""


@discord_tool(name="create_event_with_ui")
async def create_event_with_ui(title: str, date: str, time: str, run_context: RunContext) -> str:
    """Create an event and open a UI to select roles and reminder times.

    Args:
        title (str): Event title
        date (str): Date in YYYY-MM-DD format
        time (str): Time in HH:MM format
    """
    from main import parse_date, parse_time, reminder_delta, discord_ts, EventView  # deferred to avoid circular import
    ctx = get_discord_context(run_context)
    bot = get_discord_bot(run_context)

    parsed_date = parse_date(date)
    parsed_time_val = parse_time(time)
    if not parsed_date or not parsed_time_val:
        return "❌ Invalid date or time format."

    from zoneinfo import ZoneInfo
    tz = ZoneInfo(db.get_timezone(ctx["guild_id"]))
    event_dt = parsed_date.replace(hour=parsed_time_val[0], minute=parsed_time_val[1], tzinfo=tz)

    reminder_channel_id = db.get_reminder_channel(ctx["guild_id"])
    if not reminder_channel_id:
        return "⚠️ No reminder channel configured. Use `/set-reminder-channel` first."

    channel = bot.get_channel(ctx["channel_id"])
    creator = bot.get_guild(ctx["guild_id"]).get_member(ctx["author_id"])

    # EventView is Neko's native discord.ui.View — it manages role/reminder
    # selection state internally through Python callbacks.
    view = EventView(
        title=title, date=event_dt,
        announce_channel=channel,
        reminder_channel=bot.get_channel(reminder_channel_id),
        creator=creator,
    )
    await channel.send(
        f"**{title}** — {discord_ts(event_dt, 'F')}\nSelect roles and reminder times:",
        view=view,
    )
    set_discord_response(run_context, suppress_text=True)
    return ""


@discord_tool(name="delete_event")
async def delete_event(event_title: str, run_context: RunContext) -> str:
    """Delete an upcoming event by title.

    Args:
        event_title (str): Title of the event to delete (partial match supported)
    """
    ctx = get_discord_context(run_context)
    reminder_channel_id = db.get_reminder_channel(ctx["guild_id"])
    if not reminder_channel_id:
        return "⚠️ No reminder channel configured."

    events = db.get_upcoming_events(reminder_channel_id)
    matches = [e for e in events if event_title.lower() in e.title.lower()]
    if not matches:
        return f"❌ No event found matching \"{event_title}\"."
    if len(matches) > 1:
        titles = "\n".join(f"• {e.title}" for e in matches)
        return f"Multiple matches found, please be more specific:\n{titles}"

    db.delete_event(matches[0].event_id)
    return f"✅ Deleted \"{matches[0].title}\" and cancelled all reminders."
```

### Step 5 — Update `main.py`

Add the imports near the top:

```python
import os
from dango import ChatCog, create_discord_workflow, RuntimeConfig
from neko_tools import (
    set_reminder_timezone, set_reminder_channel,
    list_events, create_event_with_ui, delete_event,
)
```

At the end of `on_ready`, add:

```python
with open(os.getenv("CHAT_SYS_PROMPT_PATH", "config/chat_sys_prompt.txt"), encoding="utf-8") as f:
    chat_system_prompt = f.read()

workflow = create_discord_workflow()
runtime_config = RuntimeConfig("config/runtime.yml")
await bot.add_cog(ChatCog(
    bot,
    workflow,
    chat_system_prompt,
    runtime_config,
    extra_tools=[
        set_reminder_timezone,
        set_reminder_channel,
        list_events,
        create_event_with_ui,
        delete_event,
    ],
))
```

### Step 6 — Allow channels

Start the bot, then in each channel where you want natural-language responses, run:

```
/addchannel
```

This is `AdminCog`'s built-in command. It adds the current channel to the allowed list stored in `config/runtime.yml`. The bot will now respond to all messages in that channel, not just @mentions.

### Result

All original slash commands keep working. Users can now also interact in plain English:

| User says | Agent calls |
|-----------|-------------|
| "list upcoming events" | `list_events()` → embed |
| "create a Python study group on June 7th at 7pm" | `create_event_with_ui()` → EventView UI |
| "delete the study group event" | `delete_event("study group")` |
| "set timezone to Asia/Tokyo" | `set_reminder_timezone("Asia/Tokyo")` |

---

## Updating

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install --upgrade git+https://github.com/zhiro-labs/dango
```

Restart your bot to pick up the new version.

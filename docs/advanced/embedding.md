# Embedding into Another Bot

Because everything lives in discord.py Cogs, you can drop Dango's agent and slash commands into any existing bot with a few lines.

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
from dango.commands import ChatCog, AdminCog
from dango.utils.runtime_config import RuntimeConfig
from dango.workflow import create_discord_workflow

with open("config/chat_sys_prompt.txt", encoding="utf-8") as f:
    chat_system_prompt = f.read()

runtime_config = RuntimeConfig("config/runtime.yml")  # path is configurable; file is created automatically on first write
discord_workflow = create_discord_workflow()

await bot.add_cog(ChatCog(bot, discord_workflow, chat_system_prompt, runtime_config))
await bot.add_cog(AdminCog(bot, runtime_config))
```

Each bot gets its own `RuntimeConfig` instance, so allowed channels and users stay independent.

## Exposing your bot's commands as Agno tools

Once Dango is loaded, the Agno agent can call your existing bot commands as tools. Users can ask naturally ("play some lofi") and the agent decides when to invoke `play_music` — without breaking the original `!play` or `/play` commands.

### How it works

1. Extract the core logic of each command into a plain async function.
2. Wrap it with `@discord_tool`.
3. Pass the list of tools to `ChatCog` as `extra_tools`.

```python
from dango import ChatCog, create_discord_workflow, discord_tool, RunContext, get_discord_context

@discord_tool(name="play_music", description="Play a song or URL in the voice channel")
async def play_music(song: str, run_context: RunContext) -> str:
    """Play music in the voice channel.

    Args:
        song (str): Song name or YouTube/Spotify URL
    """
    ctx = get_discord_context(run_context)
    await music_player.play(ctx["guild_id"], song)
    return f"Now playing: {song}"

await bot.add_cog(ChatCog(
    bot,
    create_discord_workflow(),
    chat_system_prompt,
    runtime_config,
    extra_tools=[play_music],
))
```

Your original `!play` / `/play` commands keep working unchanged.

## Tool function rules

| Rule | Detail |
|---|---|
| Type hints | Required on every parameter and the return value |
| Docstring | First line = tool description shown to the LLM |
| `Args:` block | One line per parameter; Agno parses this for the tool schema |
| `run_context: RunContext` | Agno injects this automatically — not exposed to the LLM |
| Return value | Must be a `str` |
| Async or sync | Both work |

## Accessing Discord context inside a tool

```python
from dango import discord_tool, RunContext, get_discord_context

@discord_tool(name="my_tool", description="...")
async def my_tool(query: str, run_context: RunContext) -> str:
    ctx = get_discord_context(run_context)
    # ctx["channel_id"]   — int | None
    # ctx["channel_name"] — str
    # ctx["guild_id"]     — int | None  (None in DMs)
    # ctx["guild_name"]   — str
    # ctx["author_name"]  — str
    ...
```

## Updating

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install --upgrade git+https://github.com/zhiro-labs/dango
```

Restart your bot to pick up the new version.

# 🍡 Dango — Discord AI Agent

Dango is a Discord bot built on [Agno](https://docs.agno.com) that connects to pretty much any AI model provider — Google Gemini/Gemma, OpenAI, Anthropic, Groq, Ollama, and more. Drop it into a channel and it'll chat, answer questions, render tables as images, and let you tweak everything on the fly with slash commands — no restarts needed.

## What it can do

- **Use any AI provider** — set `FAST_MODEL` to `provider:model_id` (e.g. `google:gemini-2.5-flash`, `openai:gpt-4o`, `anthropic:claude-sonnet-4-20250514`, `groq:llama-3.3-70b-versatile`) and the bot figures out the right SDK and API key automatically. Google Gemini/Gemma gets some extras like Search grounding, URL context, and thinking budget.
- **Run locally** — point `FAST_MODEL` at a local Ollama or LM Studio instance and set `FAST_BASE_URL` to its address. Running the bot in Docker while the model server is on the host? Use `http://host.docker.internal:<port>` and it just works.
- **Fast + deep model pairing** — set up a cheap fast model for everyday questions and a powerful deep model for complex ones. `AUTO_ROUTE=on` switches automatically; `/deep` forces the deep model for a single message.
- **Handles errors gracefully** — retries on transient failures and falls back to your deep model when the fast one is down.
- **Understands images** — users can attach images to their messages; the bot passes them straight to the model.
- **Gets reply context** — when someone replies to a Discord message, the quoted content is woven into the prompt naturally.
- **Resolves mentions** — `@user` and `@role` tokens in history are swapped out for real display names before the model sees them.
- **Renders tables** — any markdown table in the bot's reply is auto-converted to a PNG image (with CJK font support).
- **Knows who's talking** — optionally injects the user's display name and current time into the system prompt.
- **No restarts needed** — channels, users, history limit, timezone, and activity status are all adjustable live via slash commands.
- **Fresh start anytime** — `/newchat` drops a marker so the bot ignores everything before it.
- **Workspace file access** — mount a local folder so the bot can look up files on demand (great for custom game data, knowledge bases, etc.) instead of users having to paste content into the chat.
- **Workspace context injection** — on startup the bot scans your workspace files and uses the LLM to write a short context block describing what's in there; that block gets injected into the system prompt so the bot knows when to reach for the files.
- **DuckDuckGo search** — free web search that works with any model provider (`ENABLE_DUCKDUCKGO=on`, no API key needed).
- **Website tool** — lets the bot fetch and read URLs from the conversation, for any provider (`ENABLE_WEBSITE_TOOLS=on`).
- **Custom API tools** — plug any HTTP API into the bot through the web dashboard; no code changes needed. The bot can call it with `GET`/`POST` and optional Bearer auth.
- **SQL database tools** — add a database connection string in the dashboard and the bot gets `list_tables` + `run_query` tools automatically.

## How it works

The slash commands and `on_message` listener live in two [discord.py Cogs](https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html):

| Cog | What it handles |
|---|---|
| `ChatCog` | `on_message` listener + `/newchat` + `/deep` |
| `AdminCog` | All admin slash commands |

Every message goes through a four-step Agno Workflow:

```
on_message (ChatCog listener)
    └── Agno Workflow.arun()
            ├── FetchHistory        — pull channel history, format as Agno Messages
            ├── LLMChat             — run the Agno Agent (multi-provider) with dynamic instructions
            ├── ExtractRenderTables — find markdown tables, render as PNG
            └── SendResponse        — send text + image attachments back to Discord
```

Configuration lives in two places:

| What | File | Who touches it |
|---|---|---|
| Secrets & model settings | `.env` | You (edit by hand) |
| Runtime settings | `config/runtime.yml` | The bot (via Discord slash commands) |

Both Cogs can be loaded into any discord.py bot — see [Embedding into another bot](#embedding-into-another-bot).

## Before you start

You'll need:
- A Discord bot token ([Discord Developer Portal](https://discord.com/developers/applications))
- An API key for whatever model provider you want to use (e.g. [Google AI Studio](https://aistudio.google.com), [OpenAI Platform](https://platform.openai.com/api-keys), [Anthropic Console](https://console.anthropic.com))

And depending on how you want to run it:

| Method | Extra requirements |
|---|---|
| Docker (recommended) | Anything that gives you `docker` and `docker compose` in your PATH — [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Mac/Windows), [OrbStack](https://orbstack.dev) (Mac), [Docker Engine](https://docs.docker.com/engine/install/) (Linux), or just the [Docker CLI](https://docs.docker.com/engine/install/) with any compatible runtime |
| uv (developers / low-spec machines) | Python 3.12+, [uv](https://github.com/astral-sh/uv) |

## Discord Application Setup

Before running the bot, there are a few things to configure in the [Discord Developer Portal](https://discord.com/developers/applications).

### 1. Create a Bot

If you haven't already, follow the [Discord Quick Start guide](https://discord.com/developers/docs/quick-start/getting-started#step-1-creating-an-app) to create a new application and bot. Copy the **Bot Token** — you'll need it in a moment.

### 2. Enable Privileged Gateway Intents

Go to your application → **Bot** → **Privileged Gateway Intents** and turn on both of these:

| Intent | Why |
|---|---|
| **Server Members Intent** | Needed to read user display names |
| **Message Content Intent** | Needed to read message text |

### 3. Invite the Bot

When generating an invite link (**OAuth2 → URL Generator**), make sure to include these permissions:

| Category | Permission |
|---|---|
| General | View Channels |
| Text | Send Messages |
| Text | Attach Files |
| Text | Read Message History |

## Setup

Get your Bot Token from [Discord Application Setup](#discord-application-setup) first, then pick one of the options below.

> [!TIP]
> First time running commands on a computer? Read [Running commands for the first time](#running-commands-for-the-first-time) below before picking an option — it takes 2 minutes.

### Running commands for the first time

<details>
<summary>Click to expand — even if you've never typed a command before, this takes 2 minutes</summary>

Every option in this guide requires typing a few commands into a text window on your computer. A command window (called a "terminal", "shell", "command prompt", or "PowerShell" depending on the system) lets you control your computer by typing instead of clicking. You only need the basics.

**Opening the terminal**

| System | How |
|---|---|
| macOS | ⌘ Space → type `Terminal` → Enter |
| Windows | Win key → type `Terminal` or `PowerShell` → Enter |
| Linux | Ctrl + Alt + T |

**Your computer is a tree of folders**

Files live inside folders, folders live inside other folders — it forms a tree. The terminal always operates "inside" one folder at a time.

```
~ (your home folder)
├── Downloads/
│   └── dango/        ← you'll work here
├── Documents/
└── Desktop/
```

**The prompt tells you where you are**

The text before the cursor shows your current folder. It looks different on each system, but the idea is the same:

| System | Example prompt | What it means |
|---|---|---|
| macOS / Linux | `user@computer ~ %` | currently in `~` (home folder) |
| Windows (PowerShell) | `PS C:\Users\you>` | currently in `C:\Users\you` |

On macOS/Linux, `~` is shorthand for your home folder (e.g. `/home/you`). On Windows it's usually `C:\Users\you`.

Watch the prompt update as you move around:

**macOS / Linux**
```
user@computer ~ %              (home folder)
user@computer Downloads %      (after: cd Downloads)
user@computer dango %          (after: cd dango)
```

**Windows (PowerShell)**
```
PS C:\Users\you>                        (home folder)
PS C:\Users\you\Downloads>              (after: cd Downloads)
PS C:\Users\you\Downloads\dango>        (after: cd dango)
```

**`cd` — moving between folders**

`cd` stands for "change directory" (directory = folder). The commands are almost the same on both systems, with one difference in the path separator:

| Action | macOS / Linux | Windows (PowerShell) |
|---|---|---|
| Go into a folder | `cd Downloads` | `cd Downloads` |
| Go deeper | `cd dango` | `cd dango` |
| Go up one level | `cd ..` | `cd ..` |
| Jump straight there | `cd ~/Downloads/dango` | `cd ~\Downloads\dango` |

> macOS/Linux use `/` as the separator; Windows uses `\`. PowerShell also accepts `/`, so `cd ~/Downloads/dango` usually works on Windows too.

That's it. `cd` to the right folder, then copy-paste the commands.

</details>

---

### Option 1: Let an AI set it up for you (easiest)

No special tools needed — paste the prompt below into any AI assistant:

| Assistant | How it helps |
|---|---|
| [Claude](https://claude.ai), [ChatGPT](https://chatgpt.com), [Grok](https://grok.com) | Guides you step by step — you copy-paste each command into your terminal |
| [Claude Code](https://claude.ai/code), Codex | Runs commands directly on your computer for you |

Either way, the AI explains what each step does and won't touch your tokens or API keys.

<details>
<summary>Click to show the prompt</summary>

```
I want to install the Dango Discord bot using Docker. Please go through these steps one at a time and explain what each command does before running it:

1. Check that Docker is installed and running (docker info). If not, stop and tell me to install it from https://docs.docker.com/get-docker/ before continuing.
2. Ask me where to create the project folder (suggest ~/dango as the default).
3. Create that folder and move into it.
4. Download the setup file: curl -O https://raw.githubusercontent.com/zhiro-labs/dango/main/docker-compose.yml
5. Show me the contents of docker-compose.yml before doing anything else.
6. Start the bot: docker compose up -d
7. Confirm both the "web" and "bot" containers are running: docker compose ps
8. Tell me to open http://localhost:17860 in my browser to finish setup.

Important: do NOT ask for, store, or touch any Discord tokens or API keys — the web setup wizard handles all credentials. Do not run any commands that delete files.
```

</details>

---

### Option 2: Docker (recommended)

No Python required — everything runs in a container and you configure it through the browser.

**1. Download `docker-compose.yml`**

First, navigate to the folder where you want to install Dango (create one if needed):

```bash
cd ~/Downloads       # or wherever you'd like, e.g. cd ~/dango
```

Then download the file:

```bash
curl -O https://raw.githubusercontent.com/zhiro-labs/dango/main/docker-compose.yml
```

**2. Start it up**

```bash
docker compose up -d && docker compose logs -f
```

`-d` starts the containers in the background; `logs -f` streams their output to your terminal. Press Ctrl+C to stop watching the logs — the containers keep running.

**3. Open the browser**

Head to `http://localhost:17860`. The Setup Wizard will ask for your Discord Token, model API key, and bot personality. Once you save, the bot connects to Discord automatically.

After that, you can tweak allowed channels, users, model selection, and everything else from the dashboard — no restarts needed.

---

### Option 3: uv (developers / low-spec machines)

**AI-assisted** — paste this into any AI assistant ([Claude](https://claude.ai), [ChatGPT](https://chatgpt.com), [Grok](https://grok.com), Claude Code, Codex…). Web chatbots will guide you step by step; Claude Code / Codex will run the commands for you directly.

<details>
<summary>Click to show the prompt</summary>

```
I want to install the Dango Discord bot using uv (a Python package manager). Please go through these steps one at a time and explain what each command does before running it:

1. Check that git is installed (git --version). If not, stop and tell me to install it from https://git-scm.com/downloads
2. Check that uv is installed (uv --version). If not, install it automatically:
   - Mac/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
   - Windows: tell me to visit https://docs.astral.sh/uv/getting-started/installation/
3. Ask me where to clone the project (suggest ~/dango as the default).
4. Clone and enter the folder:
   git clone https://github.com/zhiro-labs/dango <chosen-folder>
   cd <chosen-folder>
5. Install dependencies: uv sync
6. Copy the example config files:
   cp .env.example .env
   cp config/runtime.yml.example config/runtime.yml
   cp config/chat_sys_prompt.txt.example config/chat_sys_prompt.txt
7. Tell me exactly which values to fill in inside .env (DISCORD_BOT_TOKEN, FAST_API_KEY, FAST_MODEL, CHAT_SYS_PROMPT_PATH) and what each one means. Wait for me to confirm I've filled them in before continuing.
8. Start the bot: uv run main.py

Important: do NOT read, display, log, or store the contents of .env — it contains my API keys and tokens. Only tell me which variables to fill in and what they mean.
```

</details>

Or follow the steps manually:

**1. Clone and install**

Navigate to the folder where you want to install Dango, then clone the repo:

```bash
cd ~/Downloads       # or wherever you'd like
git clone https://github.com/zhiro-labs/dango
cd dango
uv sync
```

**2. Set up your `.env`**

```bash
cp .env.example .env
```

Open `.env` and fill in at least these four:

```env
DISCORD_BOT_TOKEN=your_discord_token
FAST_API_KEY=your_api_key          # matches your chosen provider
FAST_MODEL=google:gemma-4-26b-a4b-it  # format: provider:model_id
CHAT_SYS_PROMPT_PATH=config/chat_sys_prompt.txt
```

**3. Copy the config files**

```bash
cp config/runtime.yml.example config/runtime.yml
cp config/chat_sys_prompt.txt.example config/chat_sys_prompt.txt
```

Edit `config/chat_sys_prompt.txt` to give the bot its personality. Channels, user allowlist, history limit, and everything else can be changed later via Discord slash commands without restarting.

**4. Run**

```bash
uv run main.py
```

The first time you run it, the Noto Sans CJK font (~100 MB) downloads automatically for table rendering.

## Running on a VPS

The Docker setup works fine on a VPS — but the web dashboard has no login screen, so you don't want port 17860 open to the internet. Anyone who can reach it can change your Discord token and API keys.

The fix is to not expose the port at all and use an SSH tunnel instead. In your VPS firewall, make sure port 17860 is **not** open. Then whenever you want to access the dashboard, run this on your local machine:

```bash
ssh -L 17860:localhost:17860 user@your-vps-ip
```

Now open `http://localhost:17860` in your browser — it looks like a local server, but the traffic goes through SSH to your VPS. No extra software, no passwords to manage, and the port never touches the public internet.

If you'd rather not keep a terminal window open just for the tunnel, run it in the background:

```bash
ssh -fNL 17860:localhost:17860 user@your-vps-ip
```

`-f` sends it to the background, `-N` means "don't run any commands, just forward the port."

## Stopping & restarting

### Docker

**To stop the bot temporarily** (e.g. you're done for now but want to start it again later):

```bash
docker compose stop
```

The containers are paused but still exist. When you want to bring it back, just run:

```bash
docker compose start
```

That's it — your settings, history, and everything else are exactly where you left them.

> [!NOTE]
> If you're still watching logs with `docker compose logs -f`, press **Ctrl+C** first — that just stops the log view, not the bot itself. Then run `docker compose start` to bring it back.

If you ever need to fully remove the containers (e.g. to start fresh after something breaks), use `docker compose down` instead — your data stays safe, but you'll need `docker compose up -d` to bring it back.

**Computer restarted?** The containers don't come back automatically unless you've set Docker to start on login. Just `cd` into the folder where your `docker-compose.yml` lives and run `docker compose start` again.

### uv

**To stop:** press **Ctrl+C** in the terminal where `uv run main.py` is running.

**To start again:** `cd` back into the project folder and run the same command you used the first time:

```bash
uv run main.py
```

Your `.env` and everything in `config/` is still there — you don't need to set anything up again.

## Updating

### Docker

```bash
docker compose pull   # pull the latest image
docker compose up -d  # restart
```

Your data (`data/`, `config/`, `workspace/`) lives in a volume, so updates won't touch it.

### uv

```bash
git pull   # fetch the latest code
uv sync    # update packages if needed
```

Then restart the bot. `.env` and `config/` won't be overwritten.

> If you originally downloaded a zip instead of cloning, switch to `git clone` — then future updates are just one `git pull`.

## Embedding into another bot

Because everything lives in Cogs, you can drop Dango's agent and slash commands into any existing discord.py bot with just a few lines:

**1. Install**

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install git+https://github.com/zhiro-labs/dango
```

**2. Set environment variables**

`call_agent.py` reads env vars at import time, so make sure these are set before the Cogs are loaded (e.g. via `load_dotenv()` or your own config):

```env
FAST_MODEL=google:gemma-4-26b-a4b-it   # format: provider:model_id
FAST_API_KEY=your_api_key

# Optional
DEEP_MODEL=
DEEP_API_KEY=
FAST_BASE_URL=                          # custom endpoint for local/proxied models
```

See [Supported Providers](#supported-providers) for all available `provider:` prefixes.

**3. Load the Cogs in `setup_hook`**

```python
from dango.commands import ChatCog, AdminCog
from dango.utils.runtime_config import RuntimeConfig
from dango.workflow import create_discord_workflow

# Load system prompt
with open("config/chat_sys_prompt.txt", encoding="utf-8") as f:
    chat_system_prompt = f.read()

# Each bot gets its own RuntimeConfig (allowed channels, users, etc.)
runtime_config = RuntimeConfig("config/runtime.yml")

# Create the Agno workflow
discord_workflow = create_discord_workflow()

# Register Cogs — your bot now has the full agent + all slash commands
await bot.add_cog(ChatCog(bot, discord_workflow, chat_system_prompt, runtime_config))
await bot.add_cog(AdminCog(bot, runtime_config))
```

Each bot uses its own `RuntimeConfig` instance, so allowed channels and users stay independent.

### Exposing your bot's commands as Agno tools

Once Dango is loaded as a Cog, the Agno agent can call your existing commands as tools — so users can ask it naturally ("play some lofi") and the agent decides when to invoke `play_music` on their behalf, without breaking the original `!play` or `/play` commands.

**How it works**

1. Extract the core logic of each command into a plain async function.
2. Wrap it with `@discord_tool` (an alias for Agno's `@tool`).
3. Pass the list of tools to `ChatCog` as `extra_tools`.

```python
from dango import ChatCog, create_discord_workflow, discord_tool, RunContext, get_discord_context

# --- Wrap your command logic as Agno tools ---

@discord_tool(name="play_music", description="Play a song or URL in the voice channel")
async def play_music(song: str, run_context: RunContext) -> str:
    """Play music in the voice channel.

    Args:
        song (str): Song name or YouTube/Spotify URL
    """
    ctx = get_discord_context(run_context)   # channel_id, guild_id, author_name, …
    await music_player.play(ctx["guild_id"], song)
    return f"Now playing: {song}"

@discord_tool(name="set_volume", description="Set the playback volume in the voice channel")
async def set_volume(level: int) -> str:
    """Set the playback volume.

    Args:
        level (int): Volume level between 0 and 100
    """
    if not 0 <= level <= 100:
        return "Volume must be between 0 and 100."
    await music_player.set_volume(level)
    return f"Volume set to {level}%"

# --- Load ChatCog with extra tools ---

await bot.add_cog(ChatCog(
    bot,
    create_discord_workflow(),
    chat_system_prompt,
    runtime_config,
    extra_tools=[play_music, set_volume],
))
```

**Your original commands keep working unchanged.** The agent gets extra tools; Discord users still get `!play` / `/play`.

**Tool function rules**

| Rule | Detail |
|---|---|
| Type hints | Required on every parameter and the return value |
| Docstring | First line = tool description shown to the LLM |
| `Args:` block | One line per parameter; Agno parses this for the schema |
| `run_context: RunContext` | Magic parameter — Agno injects it automatically, not exposed to the LLM |
| Return value | Must be a `str` (the agent reads this as the tool result) |
| Async or sync | Both work |

**Accessing Discord context inside a tool**

Declare `run_context: RunContext` and call `get_discord_context(run_context)`:

```python
from dango import discord_tool, RunContext, get_discord_context

@discord_tool(name="my_tool", description="…")
async def my_tool(query: str, run_context: RunContext) -> str:
    ctx = get_discord_context(run_context)
    # ctx["channel_id"]   — int | None
    # ctx["channel_name"] — str
    # ctx["guild_id"]     — int | None  (None in DMs)
    # ctx["guild_name"]   — str
    # ctx["author_name"]  — str
    ...
```

**Prefix vs. slash commands — same pattern**

Both command types follow the same extraction pattern — pull the logic out of `ctx` / `interaction`, put it in a plain async function, wrap with `@discord_tool`:

```python
# Prefix command (!ban @user reason)
@bot.command()
async def ban(ctx, member: discord.Member, *, reason: str = ""):
    result = await _do_ban(ctx.guild.id, member.id, reason, ctx.author.id)
    await ctx.send(result)

# Slash command (/ban user reason)
@app_commands.command(name="ban")
async def ban_slash(interaction, member: discord.Member, reason: str = ""):
    result = await _do_ban(interaction.guild_id, member.id, reason, interaction.user.id)
    await interaction.response.send_message(result)

# Shared logic — also the Agno tool
@discord_tool(name="ban_member", description="Ban a member from the server")
async def ban_member(member_id: str, reason: str = "", run_context: RunContext = None) -> str:
    """Ban the specified member from the server.

    Args:
        member_id (str): The Discord ID of the member to ban
        reason (str): Reason for the ban (optional)
    """
    ctx = get_discord_context(run_context) if run_context else {}
    return await _do_ban(ctx.get("guild_id"), int(member_id), reason, None)

async def _do_ban(guild_id, member_id, reason, moderator_id) -> str:
    ...
    return f"Banned <@{member_id}>."
```

**Updating**

```bash
# uv
uv add git+https://github.com/zhiro-labs/dango

# pip
pip install --upgrade git+https://github.com/zhiro-labs/dango
```

Same command as installation — uv / pip handles the upgrade. Restart your bot to pick up the new version.

## Usage

### Starting a conversation

| How | What to do |
|---|---|
| **Mention** | `@BotName hello!` in any channel the bot can see |
| **Allowed channel** | Just send a message — no mention needed if the channel is in the allowed list (`/addchannel`) |
| **Direct Message** | DM the bot directly (your user ID needs to be added first with `/adduser`) |

### Continuing a conversation

The bot pulls recent channel history automatically, so you can keep replying naturally without mentioning it again. Use `/sethistorylimit` to control how far back it looks.

### Starting fresh

Use `/newchat` to drop a session marker. The bot will ignore everything before that point and treat your next message as a fresh conversation.

### Things that just happen automatically

No commands needed — these are always on (or can be turned on):

- **Table rendering** — any markdown table in the bot's reply gets rendered as a PNG for better readability
- **Google Search** — the bot searches the web when it needs current info (Gemini models; on by default via `GEMINI_SEARCH=true`)
- **URL fetching (Gemini)** — the bot reads URLs you share in chat (off by default; enable with `GEMINI_URL_CONTEXT=true`, Gemini only)
- **DuckDuckGo search** — free web search for any model provider (off by default; enable with `ENABLE_DUCKDUCKGO=on`)
- **Website tool** — fetch and read URLs from the conversation, works with any provider (off by default; enable with `ENABLE_WEBSITE_TOOLS=on`)
- **Image attachments** — attach an image to your message and the bot passes it straight to the model
- **Reply context** — when you reply to a Discord message, the quoted content is automatically included in the prompt
- **Mention resolution** — `@user` and `@role` mentions in history are replaced with real display names so the model isn't staring at raw IDs
- **Long message splitting** — if the bot's response is too long for Discord, it's split across multiple messages automatically
- **Conversation trimming** — when history gets too long, the oldest messages are dropped to stay within `CONTEXT_TOKEN_BUDGET`
- **Auto-routing** — when `AUTO_ROUTE=on` and `DEEP_MODEL` is set, complex messages (long text, code, URLs) go to the deep model automatically; simple ones stay on the fast model
- **Workspace file access** — when `ENABLE_WORKSPACE=on`, the bot can read, list, and search files inside `WORKSPACE_ROOT`; useful for custom game data or knowledge bases the agent can look up on demand
- **Swap models on the fly** — change `FAST_MODEL` or `DEEP_MODEL` to any supported provider at any time; the bot handles auth, routing, and provider-specific features without you touching the code
- **Custom endpoints** — set `FAST_BASE_URL` / `DEEP_BASE_URL` to point at a local server, self-hosted proxy, or any OpenAI-compatible API

### Adding the bot to channels (admin only)

By default the bot only responds when mentioned. Run `/addchannel` in a channel to let it respond to all messages there. `/removechannel` undoes that.

## Discord Slash Commands

### Chat

| Command | What it does |
|---|---|
| `/newchat` | Drops a `[new chat]` marker to reset conversation history |
| `/deep <message>` | Send a message and force the deep model to respond (requires `DEEP_MODEL` to be set) |

### Admin (requires Administrator permission)

| Command | What it does |
|---|---|
| `/addchannel` | Let the bot respond in the current channel |
| `/removechannel` | Remove the current channel from the allowed list |
| `/listchannels` | Show all allowed channels in this server |
| `/adduser @user` | Let a user DM the bot |
| `/removeuser @user` | Remove a user from the DM allowlist |
| `/listusers` | Show all users allowed to DM the bot |
| `/sethistorylimit <n>` | Set how many past messages are included as context |
| `/setactivity <text>` | Set the bot's Discord activity status |
| `/settimezone <tz>` | Set the bot's timezone (with autocomplete) |
| `/refreshmetadata` | Refresh display names for all saved channels and users |

## Environment Variables

### Required

| Variable | What it's for |
|---|---|
| `DISCORD_BOT_TOKEN` | Your Discord bot token |
| `FAST_MODEL` | Fast model in `provider:model_id` format (e.g. `google:gemma-4-26b-a4b-it`, `openai:gpt-4o`) |
| `FAST_API_KEY` | API key for the fast model's provider |
| `CHAT_SYS_PROMPT_PATH` | Path to the system prompt file |

### Supported Providers

Models are specified as `provider:model_id`. The bot automatically sets the right provider env var from `FAST_API_KEY` / `DEEP_API_KEY` at startup — you don't need to set `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc. yourself.

| Provider prefix | Example | Where to get the key |
|---|---|---|
| `google:` | `google:gemini-2.5-flash` | [Google AI Studio](https://aistudio.google.com/apikey) |
| `openai:` | `openai:gpt-4o` | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `anthropic:` | `anthropic:claude-sonnet-4-20250514` | [Anthropic Console](https://console.anthropic.com/) |
| `groq:` | `groq:llama-3.3-70b-versatile` | [Groq Console](https://console.groq.com/) |
| `openrouter:` | `openrouter:meta-llama/llama-3.3-70b-instruct` | [OpenRouter](https://openrouter.ai/keys) |
| `mistral:` | `mistral:mistral-large-latest` | [Mistral Console](https://console.mistral.ai/) |
| `xai:` | `xai:grok-3` | [xAI Console](https://console.x.ai/) |
| `deepseek:` | `deepseek:deepseek-chat` | [DeepSeek Platform](https://platform.deepseek.com/) |
| `ollama:` | `ollama:llama3.2` | Local (no key needed) |

For the full list of supported providers, check the [Agno model index](https://docs.agno.com/models/providers/model-index).

> **Google Gemini/Gemma only** — Search grounding, URL context, and thinking budget are exclusive to `google:` models. Those settings are hidden in the web UI and quietly ignored for everything else.

### Optional — Custom Base URL (local / proxied models)

Set `FAST_BASE_URL` or `DEEP_BASE_URL` to point requests at a different endpoint — handy for local inference servers or API gateways.

| Variable | What it does |
|---|---|
| `FAST_BASE_URL` | Custom endpoint for the fast model |
| `DEEP_BASE_URL` | Custom endpoint for the deep model |

When `*_BASE_URL` is set, the bot patches the URL directly into the provider's client (`base_url` for most providers, `host` for Ollama). The provider SDK then routes everything there.

**Bot in Docker, model on the host machine?** Use `host.docker.internal` instead of `localhost`:

| Provider | Model string | Base URL |
|---|---|---|
| Ollama | `ollama:llama3.2` | `http://host.docker.internal:11434` |
| LM Studio | `lmstudio:model-name` | `http://host.docker.internal:1234/v1` |
| vLLM | `vllm:model-name` | `http://host.docker.internal:8000/v1` |
| Any OpenAI-compatible | `openai-chat:model-name` | `http://host.docker.internal:<port>/v1` |

> **Ollama** also reads `OLLAMA_HOST` natively, so you can set that directly if you prefer.
>
> **vLLM** also reads `VLLM_BASE_URL`.
>
> **No API key needed?** Most local servers accept any non-empty string. Just set `FAST_API_KEY=local` to keep the client happy.

### Optional — Dual-model routing

| Variable | Default | What it does |
|---|---|---|
| `DEEP_MODEL` | _(off)_ | Second model in `provider:model_id` format. Leave blank to skip dual-model routing entirely. |
| `DEEP_API_KEY` | same as `FAST_API_KEY` | API key for the deep model (only needed if it's a different provider) |
| `AUTO_ROUTE` | `off` | `on` — automatically send complex messages (long text, code, URLs) to `DEEP_MODEL`; simple ones stay on `FAST_MODEL` |
| `FALLBACK_ON_ERROR` | `off` | `on` — bidirectional error fallback: fast→deep and deep→fast. Non-Gemini providers retry 2× before falling back. A `[dango-sysinfo]` note is sent when fallback fires. Works best when fast and deep use **different providers**. |

### Optional — Web search & browsing _(any provider)_

| Variable | Default | What it does |
|---|---|---|
| `ENABLE_DUCKDUCKGO` | `off` | `on` — give the bot a DuckDuckGo search tool (free, no API key, works with any provider) |
| `ENABLE_WEBSITE_TOOLS` | `off` | `on` — let the bot fetch and read URLs from the conversation (any provider; see also `GEMINI_URL_CONTEXT` for the Gemini-native version) |

### Optional — Search & Grounding _(Google models only)_

| Variable | Default | What it does |
|---|---|---|
| `GEMINI_SEARCH` | `true` | Enable Google Search grounding |
| `GEMINI_GROUNDING_THRESHOLD` | model default | Only apply grounding when confidence is below this threshold (0.0–1.0) |
| `GEMINI_URL_CONTEXT` | `false` | Let the model fetch URLs mentioned in the conversation (Gemini only; not supported by `gemma-*`) |

### Optional — Thinking _(Google models only: Gemini 2.5+ / Gemma 4)_

| Variable | Default | What it does |
|---|---|---|
| `GEMINI_THINKING_BUDGET` | model default | Token budget for reasoning; set `0` to turn thinking off |
| `GEMINI_THINKING_LEVEL` | model default | `low` or `high` |

### Optional — Context

| Variable | Default | What it does |
|---|---|---|
| `ENABLE_CONTEXTUAL_SYSTEM_PROMPT` | `on` | Inject user display names and current time into the system prompt |
| `CONTEXT_TOKEN_BUDGET` | `0` | Max tokens sent per request; oldest messages are dropped when you hit the limit. `0` means no limit. (Gemma 4 31B: ~256k \| Gemini 2.5 Flash: ~1M \| Gemini 2.5 Pro: ~2M) |

### Optional — Workspace

| Variable | Default | What it does |
|---|---|---|
| `ENABLE_WORKSPACE` | `off` | `on` — give the bot read access to a local folder via the [Agno Workspace toolkit](https://docs.agno.com/tools/toolkits/local/workspace) |
| `WORKSPACE_ROOT` | `workspace/` | Root folder the bot can access; all paths are scoped to this tree |
| `WORKSPACE_SYS_PROMPT_PATH` | `config/workspace_sys_prompt.txt` | Where to store the generated workspace context that gets injected into the system prompt |

**What files can it read?** Any file under 100,000 lines or 10 MB. In practice only plain-text formats (`.txt`, `.json`, `.yaml`, `.md`, `.csv`, etc.) are actually useful — binary files just come out as raw bytes.

**Setting the root path:** `WORKSPACE_ROOT` accepts relative or absolute paths. Relative paths are resolved to absolute at startup so the scope is always clear in logs. The default is `workspace/` — a folder inside the project that's tracked by git but whose contents are gitignored.

```env
# Default — workspace/ subfolder inside the project
WORKSPACE_ROOT=workspace

# Or point it anywhere on the host
WORKSPACE_ROOT=/home/user/game_data
```

Drop your files into `workspace/` and the bot can look them up on demand:

```
dango/
└── workspace/          ← gitignored contents, put your data files here
    ├── items.json
    ├── rules.md
    └── characters.csv
```

**Workspace context injection:** When `ENABLE_WORKSPACE=on`, the bot uses the LLM to write a short description of what's in `WORKSPACE_ROOT` and injects it into the system prompt. That way the bot knows when to reach for the workspace tool instead of making things up.

- **First run** — if `WORKSPACE_SYS_PROMPT_PATH` doesn't exist yet, it's generated and saved automatically.
- **Later runs** — the saved file is used as-is; you can edit it freely and your changes stick.
- **Live reload** — a background task checks the workspace every 30 seconds. If files change, it reloads the saved prompt (or regenerates it if you deleted it).

To customise the generated prompt, edit `config/workspace_sys_prompt.txt` after the first run.

### Optional — SQL Databases

| Variable | Default | What it does |
|---|---|---|
| `SQL_DATABASES_JSON` | `[]` | JSON array of databases the bot can query. Each entry adds `list_tables` and `run_query` tools. See [docs.agno.com/features/context](https://docs.agno.com/features/context). |

### Optional — Per-model overrides _(Google models only)_

Any `GEMINI_*` variable can be overridden for just one model using the `FAST_` or `DEEP_` prefix. Per-model values win over the shared defaults. Ignored for non-Google providers.

| Shared default | Fast model override | Deep model override |
|---|---|---|
| `GEMINI_SEARCH` | `FAST_SEARCH` | `DEEP_SEARCH` |
| `GEMINI_GROUNDING_THRESHOLD` | `FAST_GROUNDING_THRESHOLD` | `DEEP_GROUNDING_THRESHOLD` |
| `GEMINI_URL_CONTEXT` | `FAST_URL_CONTEXT` | `DEEP_URL_CONTEXT` |
| `GEMINI_THINKING_BUDGET` | `FAST_THINKING_BUDGET` | `DEEP_THINKING_BUDGET` |
| `GEMINI_THINKING_LEVEL` | `FAST_THINKING_LEVEL` | `DEEP_THINKING_LEVEL` |
| `CONTEXT_TOKEN_BUDGET` | `FAST_CONTEXT_TOKEN_BUDGET` | `DEEP_CONTEXT_TOKEN_BUDGET` |

## Project Structure

```
dango/
├── main.py                    # Discord bot entry point
├── dango/                     # Main package
│   ├── app_config.py          # Web UI config injection (data/config.yaml → os.environ)
│   ├── workflow.py            # Agno Workflow definition
│   ├── steps/
│   │   ├── fetch_history.py   # Step 1: fetch and normalize Discord history
│   │   ├── call_agent.py      # Step 2: run the Agno Agent (multi-provider)
│   │   ├── table_steps.py     # Step 3: extract tables, render as PNG
│   │   └── send_response.py   # Step 4: send text + images to Discord
│   ├── commands/
│   │   ├── chat_commands.py   # ChatCog: on_message listener, /newchat, /deep
│   │   └── admin_commands.py  # AdminCog: all admin slash commands
│   ├── tools/
│   │   └── discord_tool.py    # @discord_tool decorator + get_discord_context() helper
│   └── utils/
│       ├── build_instructions.py  # Contextual system prompt builder
│       ├── complexity_router.py   # Message complexity scoring for AUTO_ROUTE
│       ├── config_utils.py        # Env var helpers
│       ├── discord_helpers.py     # Message splitting utilities
│       ├── download_font.py       # Noto Sans CJK font downloader
│       ├── runtime_config.py      # runtime.yml reader/writer
│       └── workspace_context.py   # Workspace context injection (generate, cache, watch)
├── web/                       # FastAPI web dashboard (setup wizard + admin UI)
│   ├── config_store.py        # data/config.yaml reader/writer (Pydantic model)
│   ├── docker_api.py          # Docker Engine API wrapper for bot container control
│   ├── main.py                # FastAPI routes (/setup, /dashboard, /api/*)
│   └── templates/             # Jinja2 HTML templates
├── config/
│   ├── chat_sys_prompt.txt              # System prompt (gitignored)
│   ├── chat_sys_prompt.txt.example      # Starter template
│   ├── runtime.yml                      # Runtime config (gitignored)
│   ├── runtime.yml.example              # Default runtime config
│   └── workspace_sys_prompt.txt         # Generated workspace context (gitignored)
├── assets/fonts/              # CJK fonts for table rendering
└── tests/                     # Unit tests
```

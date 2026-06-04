# Dango

**Dango** is a Discord bot built on [Agno](https://docs.agno.com) that connects to virtually any AI model provider — Google Gemini/Gemma, OpenAI, Anthropic, Groq, Ollama, and more. Drop it into a channel and it will chat, answer questions, render tables as images, and let you tweak everything on the fly with slash commands — no restarts needed.

## Highlights

| Feature | Description |
|---|---|
| **Any AI provider** | `provider:model_id` format — the bot sets up the right SDK and API key automatically |
| **Dual-model routing** | Pair a fast model for simple messages and a deep model for complex ones; `AUTO_ROUTE=on` switches automatically |
| **Local models** | Point `FAST_BASE_URL` at Ollama, LM Studio, or vLLM and run everything offline |
| **Table rendering** | Markdown tables in replies are auto-converted to PNG images (CJK font support included) |
| **Web dashboard** | Browser-based setup wizard and admin UI — no config file editing needed |
| **No restarts** | Channels, users, history limit, timezone, and activity are all adjustable live via slash commands |
| **Image support** | Attach images to messages; the bot passes them straight to the model |
| **Tools** | Web search (DuckDuckGo), URL fetching, workspace file access, custom APIs, SQL databases |
| **Embeddable** | Drop the Cogs into any existing discord.py bot in a few lines |

## Quick Start

Pick the path that fits your setup:

<div class="grid cards" markdown>

- **Docker** (recommended)

    No Python required. Configure everything from the browser.

    [Docker Setup →](getting-started/docker.md)

- **uv** (developers)

    Clone, sync, fill in `.env`, run.

    [uv Setup →](getting-started/uv.md)

</div>

Either way, start with [Discord Setup](getting-started/discord-setup.md) to create your bot token.

## Project Structure

```
dango/                         # repo root
├── main.py                    # Entry point
├── dango/                     # Python package
│   ├── app_config.py          # Web UI config injection
│   ├── workflow.py            # Agno Workflow definition
│   ├── steps/                 # 4-step pipeline
│   │   ├── fetch_history.py
│   │   ├── call_agent.py      # Multi-provider LLM call
│   │   ├── table_steps.py     # Table → PNG rendering
│   │   └── send_response.py
│   ├── commands/
│   │   ├── chat_commands.py   # ChatCog: on_message, /newchat, /deep
│   │   └── admin_commands.py  # AdminCog: all admin slash commands
│   ├── tools/
│   │   └── discord_tool.py    # @discord_tool decorator
│   └── utils/
├── web/                       # FastAPI dashboard
├── config/                    # System prompt & runtime config
└── tests/
```

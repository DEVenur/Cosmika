# Environment Variables

Configuration lives in `.env` (uv path) or `data/config.yaml` (Docker / web dashboard). Both map to the same environment variables described here.

## Required

| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Your Discord bot token |
| `FAST_MODEL` | Model in `provider:model_id` format (e.g. `google:gemma-4-26b-a4b-it`) |
| `FAST_API_KEY` | API key for the fast model's provider |
| `CHAT_SYS_PROMPT_PATH` | Path to the system prompt file (uv path only) |

## Dual-model routing

| Variable | Default | Description |
|---|---|---|
| `DEEP_MODEL` | _(off)_ | Second model in `provider:model_id` format. Leave blank to disable routing. |
| `DEEP_API_KEY` | same as `FAST_API_KEY` | API key for the deep model (only needed for a different provider) |
| `AUTO_ROUTE` | `off` | `on` — send complex messages to `DEEP_MODEL` automatically |
| `FALLBACK_ON_ERROR` | `off` | `on` — fall back to the other model when one returns an error |

See [Model Providers & Routing](../features/models.md) for details on how routing works.

## Custom endpoints

Useful for local inference servers (Ollama, LM Studio, vLLM) or API gateways.

| Variable | Description |
|---|---|
| `FAST_BASE_URL` | Custom endpoint for the fast model |
| `DEEP_BASE_URL` | Custom endpoint for the deep model |

When the bot runs in Docker and the model server runs on the host, use `host.docker.internal` instead of `localhost`:

| Server | Model string | Base URL |
|---|---|---|
| Ollama | `ollama:llama3.2` | `http://host.docker.internal:11434` |
| LM Studio | `lmstudio:model-name` | `http://host.docker.internal:1234/v1` |
| vLLM | `vllm:model-name` | `http://host.docker.internal:8000/v1` |
| Any OpenAI-compatible | `openai-chat:model-name` | `http://host.docker.internal:<port>/v1` |

## Bot behaviour

| Variable | Default | Description |
|---|---|---|
| `ENABLE_CONTEXTUAL_SYSTEM_PROMPT` | `on` | Inject user display names and current time into the system prompt |
| `CONTEXT_TOKEN_BUDGET` | `0` | Max input tokens per request; oldest messages are dropped when exceeded. `0` = no limit. |

## Web search & browsing

| Variable | Default | Description |
|---|---|---|
| `ENABLE_DUCKDUCKGO` | `off` | `on` — free DuckDuckGo search, works with any provider |
| `ENABLE_WEBSITE_TOOLS` | `off` | `on` — let the bot fetch and read URLs from the conversation |

## Workspace

| Variable | Default | Description |
|---|---|---|
| `ENABLE_WORKSPACE` | `off` | `on` — give the bot read access to a local folder |
| `WORKSPACE_ROOT` | `workspace/` | Root folder the bot can access |
| `WORKSPACE_SYS_PROMPT_PATH` | `config/workspace_sys_prompt.txt` | Where to store the generated workspace context |

See [Tools](../features/tools.md) for more on workspace behaviour.

## Custom tools

| Variable | Default | Description |
|---|---|---|
| `ENABLE_CUSTOM_APIS` | `off` | `on` — enable HTTP API tools defined in `CUSTOM_APIS_JSON` |
| `CUSTOM_APIS_JSON` | `[]` | JSON array of REST API configs (`name`, `base_url`, `api_key`, `description`) |
| `ENABLE_SQL_DATABASES` | `off` | `on` — enable SQL tools defined in `SQL_DATABASES_JSON` |
| `SQL_DATABASES_JSON` | `[]` | JSON array of database configs (`name`, `db_url`, `description`) |

## Google / Gemini-specific

These apply to `google:` models only. Ignored for all other providers.

### Search & grounding

| Variable | Default | Description |
|---|---|---|
| `GEMINI_SEARCH` | `true` | Enable Google Search grounding |
| `GEMINI_GROUNDING_THRESHOLD` | model default | Apply grounding only when confidence is below this value (0.0–1.0) |
| `GEMINI_URL_CONTEXT` | `false` | Let the model fetch URLs mentioned in the conversation (Gemini only; not `gemma-*`) |

### Thinking (Gemini 2.5+ / Gemma 4)

| Variable | Default | Description |
|---|---|---|
| `GEMINI_THINKING_BUDGET` | model default | Token budget for reasoning; `0` disables thinking |
| `GEMINI_THINKING_LEVEL` | model default | `low` or `high` |

### Per-model overrides

Any `GEMINI_*` variable can be overridden for just one model using the `FAST_` or `DEEP_` prefix:

| Shared default | Fast override | Deep override |
|---|---|---|
| `GEMINI_SEARCH` | `FAST_SEARCH` | `DEEP_SEARCH` |
| `GEMINI_GROUNDING_THRESHOLD` | `FAST_GROUNDING_THRESHOLD` | `DEEP_GROUNDING_THRESHOLD` |
| `GEMINI_URL_CONTEXT` | `FAST_URL_CONTEXT` | `DEEP_URL_CONTEXT` |
| `GEMINI_THINKING_BUDGET` | `FAST_THINKING_BUDGET` | `DEEP_THINKING_BUDGET` |
| `GEMINI_THINKING_LEVEL` | `FAST_THINKING_LEVEL` | `DEEP_THINKING_LEVEL` |
| `CONTEXT_TOKEN_BUDGET` | `FAST_CONTEXT_TOKEN_BUDGET` | `DEEP_CONTEXT_TOKEN_BUDGET` |

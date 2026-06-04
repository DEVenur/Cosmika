# Troubleshooting

## Bot doesn't respond at all

**Check 1 — `DISCORD_BOT_TOKEN`**

Look for a login error in the startup logs. A wrong token produces:

```
discord.errors.LoginFailure: Improper token has been passed.
```

Double-check the token in `.env` (no extra spaces, no quotes).

**Check 2 — channel not added**

By default the bot only responds when `@mentioned`. Run `/addchannel` in the channel where you want it to respond to all messages.

**Check 3 — `FAST_API_KEY` error**

A bad API key produces an HTTP 401 or 403 from the model provider. Look for lines like:

```
⚠️  [call_discord_agent] google:gemini-2.0-flash failed ...
```

followed by the provider's error message. Verify the key in `.env` and that it matches the provider used in `FAST_MODEL`.

---

## `/addchannel` has no visible effect

`AdminCog` responds to slash commands with an ephemeral reply — the confirmation is visible **only to you** and disappears after a few seconds. If you don't see the reply at all:

- Confirm the bot has the `applications.commands` scope in Discord
- Confirm the user running the command has the **Administrator** permission
- Try `/listchannels` to verify whether the channel was added

---

## Feature doesn't turn on despite setting the env var

The most common cause is using `true`/`false` for a variable that expects `on`/`off`, or vice versa.

| Variable group | Correct format |
|---|---|
| `ENABLE_*`, `AUTO_ROUTE`, `FALLBACK_ON_ERROR`, `ENABLE_CONTEXTUAL_SYSTEM_PROMPT` | `on` / `off` |
| `GEMINI_SEARCH`, `GEMINI_URL_CONTEXT`, `GEMINI_THINKING_*` | `true` / `false` |

Incorrect values fail **silently** — no error is logged and the feature is simply not enabled.

---

## Gemini Search and DuckDuckGo both enabled

`GEMINI_SEARCH=true` (Google Search grounding) and `ENABLE_DUCKDUCKGO=on` (DuckDuckGo tool) can coexist, but they operate differently:

- **Gemini Search grounding** is applied by the Gemini API server; the model blends web results automatically into its response.
- **DuckDuckGo** is a tool the model can call; it returns raw search results that the model then synthesises.

When both are active, the model may call DuckDuckGo even when grounding is already enabled, potentially increasing latency. For `google:` models, prefer `GEMINI_SEARCH=true` alone and leave `ENABLE_DUCKDUCKGO=off`.

---

## `FALLBACK_ON_ERROR` fires — what does the message look like?

When fallback is triggered, a `[dango-sysinfo]` blockquote is prepended to the response in Discord:

```
> [dango-sysinfo] ⚡ google:gemini-2.0-flash failed — response served by google:gemini-2.5-pro.
```

This message is visible to users but is stripped from LLM history so it does not affect subsequent conversation context.

---

## `CUSTOM_APIS_JSON` tool is not registered

The most common cause is a multi-line JSON value in `.env`. The parser reads the variable as a single line and cannot parse fragmented JSON.

Compress to one line:

```bash
echo '[{"name":"weather","base_url":"https://api.example.com","description":"Weather"}]' | jq -c '.'
```

Then paste the output as the value in `.env`. See [Tools — Custom API Tools](features/tools.md#custom-api-tools) for details.

---

## Testing tool logic without starting the full bot

You can call `@discord_tool` functions directly in a test script — they are regular Python async functions. The `run_context` argument is only needed when the function actually calls helpers like `get_discord_context()`. For pure logic tests, pass `None`:

```python
import asyncio
from neko_tools import delete_event

async def test():
    result = await delete_event.__wrapped__("study group", run_context=None)
    print(result)

asyncio.run(test())
```

For functions that use Discord context, mock `run_context` by constructing a minimal object or by calling `get_discord_context` with a fake `session_state`. Unit-testing the tool logic in isolation means you do not need a running Discord bot for most development iterations.

---

## Workspace context not injected

If `ENABLE_WORKSPACE=on` is set but the workspace instructions never appear in the system prompt:

1. **Empty folder** — if `WORKSPACE_ROOT` contains no `.md` or `.txt` files, context generation is skipped entirely.
2. **Generation failed** — look for `⚠️ Workspace context generation returned empty` in the startup logs. This means the LLM returned an empty response; the context file was not written.
3. **Cache is stale** — edit or touch a file in the workspace folder; the background watcher regenerates the context within 30 seconds.

# Tools

## Web Search (DuckDuckGo)

Free web search that works with any model provider — no API key required.

```env
ENABLE_DUCKDUCKGO=on
```

The bot gets a `duckduckgo_search` tool and uses it when the model decides a web search would help answer a question.

## Website Tool

Lets the bot fetch and read URLs that appear in the conversation.

```env
ENABLE_WEBSITE_TOOLS=on
```

Works with any provider. For Google Gemini, there's also a native alternative — `GEMINI_URL_CONTEXT=true` — which is more tightly integrated with the model but only works for `google:` providers and not `gemma-*` models.

## Workspace File Access

Mount a local folder and the bot can read, list, and search files inside it. Good for custom game data, knowledge bases, or any content you want the bot to look up on demand.

```env
ENABLE_WORKSPACE=on
WORKSPACE_ROOT=workspace    # relative or absolute path
```

The default `workspace/` folder is inside the project directory. Its contents are gitignored.

```
dango/
└── workspace/
    ├── items.json
    ├── rules.md
    └── characters.csv
```

**What files can it read?** Any file under 100,000 lines or 10 MB. Plain-text formats (`.txt`, `.json`, `.yaml`, `.md`, `.csv`) are most useful — binary files come out as raw bytes.

### Workspace context injection

On startup, the bot uses the LLM to write a short description of `WORKSPACE_ROOT` contents and injects it into the system prompt. That way the bot knows when to reach for the workspace tool.

- **First run**: the context is generated and saved to `WORKSPACE_SYS_PROMPT_PATH` (default: `config/workspace_sys_prompt.txt`)
- **Later runs**: the saved file is used as-is; edit it freely and your changes stick
- **Live reload**: a background task checks the workspace every 30 seconds and reloads if files change

## Custom API Tools

Plug any HTTP API into the bot through the web dashboard — no code changes needed.

```env
ENABLE_CUSTOM_APIS=on
CUSTOM_APIS_JSON=[{"name": "weather", "base_url": "https://api.example.com", "api_key": "secret", "description": "Weather API"}]
```

Each entry creates a tool named `call_<name>_api`. The bot can call it with `GET`/`POST`, optional query params, JSON body, and Bearer auth pre-configured.

Fields per entry:

| Field | Required | Description |
|---|---|---|
| `name` | yes | Unique name; becomes part of the tool function name |
| `base_url` | yes | Base URL of the API |
| `api_key` | no | Sent as `Authorization: Bearer <key>` |
| `description` | no | Shown to the model to help it decide when to call this tool |

The Docker dashboard provides a UI for managing these without editing JSON directly.

## SQL Databases

Add a database connection string and the bot gets `list_tables` and `run_query` tools automatically. Queries are read-only.

```env
ENABLE_SQL_DATABASES=on
SQL_DATABASES_JSON=[{"name": "analytics", "db_url": "postgresql://user:pass@host/dbname", "description": "Analytics DB"}]
```

Supported databases: PostgreSQL, MySQL, SQLite, and anything SQLAlchemy supports.

Fields per entry:

| Field | Required | Description |
|---|---|---|
| `name` | yes | Unique name for this database |
| `db_url` | yes | SQLAlchemy connection string |
| `description` | no | Helps the model understand what data is available |

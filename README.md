# 🍡 Dango — Discord AI Agent

把任何 AI 模型接進你的 Discord，五分鐘搞定。

Gemini、GPT-4o、Claude、Llama、本地的 Ollama——通通支援，切換只要改一行設定。不需要重啟，不需要動程式碼，在 Discord 下指令就能調整一切。

**[📖 完整文件](https://zhiro-labs.github.io/dango)** · [快速開始](#setup) · [功能介紹](#features)

---

## Why Dango?

大多數 Discord AI Bot 只綁定一家服務商，換模型就要重寫。Dango 不一樣——它把 provider 跟邏輯分開，今天用免費的 Gemma，明天換成 GPT-4o，後天跑本地 Ollama，設定一改即生效。

幾個讓人用了就回不去的功能：

- **雙模型路由** — 簡單問題走快模型省錢，複雜問題自動切深度模型。[了解更多 →](https://zhiro-labs.github.io/dango/features/models/)
- **Table 變圖片** — Bot 回覆的 Markdown 表格自動渲染成 PNG，手機上也看得清楚（支援中日韓字型）
- **Workspace 知識庫** — 把資料夾掛進去，Bot 就能查你的自訂資料，不用每次貼給它
- **瀏覽器設定介面** — Docker 啟動後開 `localhost:17860`，什麼都能改，完全不用碰終端機
- **可嵌入任何 Bot** — 整個 Agent 是標準 discord.py Cog，三行程式碼塞進你現有的 Bot

---

## Setup

需要準備：Discord Bot Token（[怎麼建？](https://zhiro-labs.github.io/dango/getting-started/discord-setup/)）+ 任意 AI provider 的 API Key。

### 🐳 Docker（推薦）

```bash
curl -O https://raw.githubusercontent.com/zhiro-labs/dango/main/docker-compose.yml
docker compose up -d
```

開啟 `http://localhost:17860`，跟著設定精靈走就好。[完整說明 →](https://zhiro-labs.github.io/dango/getting-started/docker/)

### 🐍 uv（開發者）

```bash
git clone https://github.com/zhiro-labs/dango && cd dango
uv sync
cp .env.example .env  # 填入 DISCORD_BOT_TOKEN、FAST_MODEL、FAST_API_KEY
uv run main.py
```

[完整說明 →](https://zhiro-labs.github.io/dango/getting-started/uv/)

---

## Features

| 功能 | 說明 |
|---|---|
| 任意 AI Provider | `google:gemini-2.5-flash`、`openai:gpt-4o`、`anthropic:claude-sonnet-4`、`ollama:llama3.2`… |
| 雙模型 AUTO_ROUTE | 複雜度自動分流，`/deep` 強制用深度模型 |
| 本地模型 | Ollama / LM Studio / vLLM，設 `FAST_BASE_URL` 即可 |
| 圖片理解 | 附圖直接送給模型 |
| 網路搜尋 | DuckDuckGo（免費）或 Gemini 原生 Google Search |
| Custom API / SQL | 在 Dashboard 貼 URL 就能讓 Bot 呼叫你的 API 或查資料庫 |
| 無重啟設定 | 頻道、用戶、歷史長度、時區——全部 slash command 即時調整 |

[→ 完整功能說明](https://zhiro-labs.github.io/dango/features/models/)

---

## 嵌入你現有的 Bot

整個 Agent 是標準 Cog，三行載入：

```python
from dango.commands import ChatCog, AdminCog
await bot.add_cog(ChatCog(bot, create_discord_workflow(), system_prompt, runtime_config))
await bot.add_cog(AdminCog(bot, runtime_config))
```

還可以把你 Bot 的指令包成 Agno tool，讓 AI 自己決定什麼時候呼叫。[完整教學 →](https://zhiro-labs.github.io/dango/advanced/embedding/)

---

## 文件

**[zhiro-labs.github.io/dango](https://zhiro-labs.github.io/dango)**

| | |
|---|---|
| [Discord 設定](https://zhiro-labs.github.io/dango/getting-started/discord-setup/) | [環境變數參考](https://zhiro-labs.github.io/dango/configuration/env-vars/) |
| [Docker 安裝](https://zhiro-labs.github.io/dango/getting-started/docker/) | [Slash Commands](https://zhiro-labs.github.io/dango/usage/commands/) |
| [模型 & 路由](https://zhiro-labs.github.io/dango/features/models/) | [嵌入其他 Bot](https://zhiro-labs.github.io/dango/advanced/embedding/) |

---

Built with [Agno](https://docs.agno.com) · [discord.py](https://discordpy.readthedocs.io)

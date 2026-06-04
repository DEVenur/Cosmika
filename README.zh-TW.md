# 🍡 Dango — Discord AI Agent

把任何 AI 模型接進你的 Discord，五分鐘搞定。

Gemini、GPT-4o、Claude、Llama、本地 Ollama——通通支援，換模型只要改一行設定。不需要重啟，不需要動程式碼，在 Discord 下指令就能調整一切。

**[📖 完整文件](https://zhiro-labs.github.io/dango)** · [English README](README.md)

---

## 能做什麼

- **支援任意 AI Provider** — 設定 `FAST_MODEL` 為 `provider:model_id`（例如 `google:gemini-2.5-flash`、`openai:gpt-4o`、`anthropic:claude-sonnet-4-20250514`、`groq:llama-3.3-70b-versatile`），Bot 自動找對應的 SDK 和 API Key。
- **跑本地模型** — 把 `FAST_MODEL` 指向本地的 Ollama 或 LM Studio，設好 `FAST_BASE_URL` 就能用。Bot 在 Docker 裡、模型在主機上？用 `http://host.docker.internal:<port>` 直接通。
- **看得懂圖片** — 使用者附上圖片，Bot 直接送給模型處理。
- **理解 Discord 回覆** — 有人回覆某則訊息時，被引用的內容會自然地融入 prompt。
- **表格變圖片** — Bot 回覆裡的 Markdown 表格自動渲染成 PNG（支援中日韓字型），手機上也看得清楚。

不只這些，還可以幫它裝上工具：

- **Workspace 知識庫** — 掛載本地資料夾，Bot 就成了整個團隊的活知識庫。自訂遊戲資料、共用文件、社群 Wiki、內部 FAQ——成員直接問，Bot 從你的檔案裡回答。
- **DuckDuckGo 搜尋** — 免費網路搜尋，支援所有 Provider（`ENABLE_DUCKDUCKGO=on`，不需 API Key）。
- **網頁工具** — 讓 Bot 抓取並閱讀對話中出現的 URL，支援所有 Provider。
- **Custom API 工具** — 在 Web Dashboard 貼上 URL，Bot 就能呼叫你的 API，不需要改程式碼。
- **SQL 資料庫工具** — 貼上連線字串，Bot 自動獲得 `list_tables` 和 `run_query` 工具。

已經有 Discord Bot 了嗎？

- **可嵌入** — 整個功能是標準 discord.py Cog，幾行程式碼就能把 Dango 的 Agent 和 slash commands 塞進現有 Bot。
- **指令變工具** — 用 `@discord_tool` 包裝你 Bot 現有的指令，Agent 就能代替使用者呼叫它們。原本的指令完全不受影響——舉例來說，`!play` / `/play` 還是照常運作，但使用者現在也可以直接說「放點輕音樂」，Agent 自己決定什麼時候呼叫。

## 開始之前

你需要準備：
- Discord Bot Token（[Discord 開發者平台](https://discord.com/developers/applications)）
- 你選擇的 AI Provider 的 API Key（例如 [Google AI Studio](https://aistudio.google.com)、[OpenAI Platform](https://platform.openai.com/api-keys)、[Anthropic Console](https://console.anthropic.com)）

| 安裝方式 | 額外需求 |
|---|---|
| Docker（推薦） | [Docker Desktop](https://www.docker.com/products/docker-desktop/)（Mac/Windows）、[OrbStack](https://orbstack.dev)（Mac）或 [Docker Engine](https://docs.docker.com/engine/install/)（Linux） |
| uv（開發者 / 低規格機器） | Python 3.12+、[uv](https://github.com/astral-sh/uv) |

## Discord 應用程式設定

### 1. 建立 Bot

前往 [Discord 開發者平台](https://discord.com/developers/applications)建立新應用程式和 Bot，複製 **Bot Token**，等等會用到。

### 2. 開啟特殊 Gateway Intent

進入你的應用程式 → **Bot** → **Privileged Gateway Intents**，把這兩個都開啟：

| Intent | 用途 |
|---|---|
| **Server Members Intent** | 讀取用戶的顯示名稱 |
| **Message Content Intent** | 讀取訊息內容 |

### 3. 邀請 Bot 進伺服器

在 **OAuth2 → URL Generator** 產生邀請連結，權限要包含：

| 類別 | 權限 |
|---|---|
| 一般 | View Channels（查看頻道） |
| 文字 | Send Messages（傳送訊息） |
| 文字 | Attach Files（附加檔案） |
| 文字 | Read Message History（讀取訊息歷史） |

## 安裝

先完成 [Discord 應用程式設定](#discord-應用程式設定)，再選以下其中一種方式。

> [!TIP]
> 第一次在電腦上輸入指令？在選安裝方式之前，先看一下下面的[第一次使用終端機](#第一次使用終端機)——只需要 2 分鐘。

### 第一次使用終端機

<details>
<summary>點開展開 — 就算完全沒用過，2 分鐘就夠了</summary>

這份指南的每個選項都需要在電腦上輸入幾行指令。輸入指令的視窗叫做「終端機」（macOS/Linux）或「命令提示字元 / PowerShell」（Windows）。你只需要學會最基本的操作。

**開啟終端機**

| 系統 | 方法 |
|---|---|
| macOS | ⌘ 空白鍵 → 輸入 `Terminal` → Enter |
| Windows | Win 鍵 → 輸入 `Terminal` 或 `PowerShell` → Enter |
| Linux | Ctrl + Alt + T |

**電腦是一棵資料夾樹**

```
~ （你的家目錄）
├── Downloads/
│   └── dango/        ← 你會在這裡工作
├── Documents/
└── Desktop/
```

**`cd` — 在資料夾之間移動**

| 動作 | macOS / Linux | Windows (PowerShell) |
|---|---|---|
| 進入資料夾 | `cd Downloads` | `cd Downloads` |
| 回上一層 | `cd ..` | `cd ..` |
| 直接跳過去 | `cd ~/Downloads/dango` | `cd ~\Downloads\dango` |

就這樣。`cd` 到正確的資料夾，再複製貼上指令。

</details>

---

### 選項一：請 AI 幫你安裝（最簡單）

不需要任何工具——把下面的 prompt 貼給任何 AI 助手：

| 助手 | 如何幫你 |
|---|---|
| [Claude](https://claude.ai)、[ChatGPT](https://chatgpt.com)、[Grok](https://grok.com) | 一步一步引導你，你把指令複製貼到終端機執行 |
| [Claude Code](https://claude.ai/code)、Codex | 直接在你的電腦上執行指令 |

<details>
<summary>點開查看 prompt</summary>

```
我想用 Docker 安裝 Dango Discord Bot。請一步一步進行，每個指令執行前先說明它做什麼：

1. 確認 Docker 已安裝且正在執行（docker info）。如果沒有，停下來告訴我去 https://docs.docker.com/get-docker/ 安裝後再繼續。
2. 問我要在哪裡建立專案資料夾（建議預設用 ~/dango）。
3. 建立該資料夾並進入。
4. 下載設定檔：curl -O https://raw.githubusercontent.com/zhiro-labs/dango/main/docker-compose.yml
5. 在做任何其他事之前，先顯示 docker-compose.yml 的內容給我看。
6. 啟動 Bot：docker compose up -d
7. 確認「web」和「bot」兩個容器都在執行：docker compose ps
8. 告訴我在瀏覽器開啟 http://localhost:17860 完成設定。

重要：請勿要求、儲存或碰觸任何 Discord Token 或 API Key——網頁設定精靈會處理所有憑證。不要執行任何刪除檔案的指令。
```

</details>

---

### 選項二：Docker（推薦）

不需要 Python，全部跑在容器裡，透過瀏覽器設定。

**1. 下載 `docker-compose.yml`**

```bash
cd ~/Downloads       # 或任何你想要的地方
curl -O https://raw.githubusercontent.com/zhiro-labs/dango/main/docker-compose.yml
```

**2. 啟動**

```bash
docker compose up -d && docker compose logs -f
```

`-d` 讓容器在背景執行；`logs -f` 把輸出串流到終端機。按 Ctrl+C 停止看 log，容器還是繼續跑。

**3. 開啟瀏覽器**

前往 `http://localhost:17860`。設定精靈會引導你填入 Discord Token、模型 API Key 和 Bot 個性。儲存後 Bot 自動連線到 Discord。

---

### 選項三：uv（開發者 / 低規格機器）

**請 AI 協助** — 把這個 prompt 貼給任何 AI 助手：

<details>
<summary>點開查看 prompt</summary>

```
我想用 uv（Python 套件管理工具）安裝 Dango Discord Bot。請一步一步進行，每個指令執行前先說明它做什麼：

1. 確認 git 已安裝（git --version）。如果沒有，停下來告訴我去 https://git-scm.com/downloads 安裝。
2. 確認 uv 已安裝（uv --version）。如果沒有，自動安裝：
   - Mac/Linux：curl -LsSf https://astral.sh/uv/install.sh | sh
   - Windows：告訴我去 https://docs.astral.sh/uv/getting-started/installation/
3. 問我要把專案 clone 到哪裡（建議預設用 ~/dango）。
4. Clone 並進入資料夾：
   git clone https://github.com/zhiro-labs/dango <選擇的資料夾>
   cd <選擇的資料夾>
5. 安裝依賴：uv sync
6. 複製範例設定檔：
   cp .env.example .env
   cp config/runtime.yml.example config/runtime.yml
   cp config/chat_sys_prompt.txt.example config/chat_sys_prompt.txt
7. 告訴我 .env 裡需要填哪些值（DISCORD_BOT_TOKEN、FAST_API_KEY、FAST_MODEL、CHAT_SYS_PROMPT_PATH）以及每個的用途。等我確認填好後再繼續。
8. 啟動 Bot：uv run main.py

重要：請勿讀取、顯示、記錄或儲存 .env 的內容——裡面有我的 API Key 和 Token。只告訴我要填哪些變數以及它們的意思。
```

</details>

或手動操作：

**1. Clone 並安裝**

```bash
cd ~/Downloads       # 或任何你想要的地方
git clone https://github.com/zhiro-labs/dango
cd dango
uv sync
```

**2. 設定 `.env`**

```bash
cp .env.example .env
```

打開 `.env` 填入至少這四個：

```env
DISCORD_BOT_TOKEN=你的_discord_token
FAST_API_KEY=你的_api_key
FAST_MODEL=google:gemma-4-26b-a4b-it   # 格式：provider:model_id
CHAT_SYS_PROMPT_PATH=config/chat_sys_prompt.txt
```

**3. 複製設定檔**

```bash
cp config/runtime.yml.example config/runtime.yml
cp config/chat_sys_prompt.txt.example config/chat_sys_prompt.txt
```

編輯 `config/chat_sys_prompt.txt` 設定 Bot 的個性。頻道、用戶白名單、歷史長度等等之後都可以透過 slash command 更改，不需重啟。

**4. 執行**

```bash
uv run main.py
```

第一次執行會自動下載 Noto Sans CJK 字型（~100 MB），用來渲染表格圖片。

## 停止與重啟

### Docker

```bash
docker compose stop    # 暫停（保留所有資料）
docker compose start   # 恢復
```

要完全移除容器（例如重新開始）：`docker compose down`——資料會保留，但需要 `docker compose up -d` 才能重新啟動。

> [!NOTE]
> **電腦重開機了？** 容器不會自動恢復。`cd` 到有 `docker-compose.yml` 的資料夾，執行 `docker compose start`。

### uv

**停止：** 在執行 `uv run main.py` 的終端機按 Ctrl+C。

**重新啟動：**
```bash
uv run main.py
```

## 更新

### Docker

```bash
docker compose pull && docker compose up -d
```

你的資料（`data/`、`config/`、`workspace/`）存在 volume 裡，不會被更新覆蓋。

### uv

```bash
git pull && uv sync
```

重啟 Bot 即可。`.env` 和 `config/` 不會被覆蓋。

## 部署到 VPS

Docker 安裝在 VPS 上完全可行，但 Web Dashboard 沒有登入畫面——不要把 `17860` 埠開放到網際網路。解法是 SSH 通道：防火牆封鎖該埠，需要使用 Dashboard 時在本機做 port forwarding。

```bash
ssh -L 17860:localhost:17860 user@你的vps-ip
```

[→ 完整 VPS 部署指南](https://zhiro-labs.github.io/dango/advanced/vps/)

## 嵌入其他 Bot

所有功能都是標準 discord.py Cog，可以把 Dango 的 Agent 和 slash commands 塞進現有的 Bot。你也可以把自己 Bot 的指令包成 Agno tool——使用者自然地提問（「放點輕音樂」），Agent 自己決定什麼時候呼叫。

```bash
uv add git+https://github.com/zhiro-labs/dango
```

[→ 完整嵌入指南](https://zhiro-labs.github.io/dango/advanced/embedding/)

## 使用方法

### 開始對話

| 方式 | 操作 |
|---|---|
| **提及** | 在任何 Bot 看得到的頻道輸入 `@BotName 你好！` |
| **允許頻道** | 直接傳訊息——如果頻道在允許清單裡（`/addchannel`），不需要提及 Bot |
| **私訊** | 直接 DM Bot（你的用戶 ID 需要先用 `/adduser` 加入允許清單） |

用 `/newchat` 插入分隔標記重置對話。Bot 會忽略標記之前的所有訊息。

### Slash Commands

| 指令 | 功能 |
|---|---|
| `/newchat` | 重置對話歷史 |
| `/deep <訊息>` | 強制使用深度模型回覆這則訊息 |
| `/addchannel` / `/removechannel` | 管理允許頻道（需管理員） |
| `/adduser` / `/removeuser` | 管理私訊白名單（需管理員） |
| `/sethistorylimit <n>` | 設定上下文訊息數量（需管理員） |
| `/settimezone <時區>` | 設定 Bot 時區，支援自動補全（需管理員） |
| `/setactivity <文字>` | 設定 Discord 狀態訊息（需管理員） |

[→ 完整 Slash Command 參考](https://zhiro-labs.github.io/dango/usage/commands/)

## 文件

完整文件在 **[zhiro-labs.github.io/dango](https://zhiro-labs.github.io/dango)**

| 頁面 | 內容 |
|---|---|
| [環境變數](https://zhiro-labs.github.io/dango/configuration/env-vars/) | 所有設定選項與預設值——模型、路由、工具、Gemini 專屬設定 |
| [模型 Provider 與路由](https://zhiro-labs.github.io/dango/features/models/) | 支援的 Provider、雙模型 AUTO_ROUTE、錯誤回退、本地模型 |
| [工具](https://zhiro-labs.github.io/dango/features/tools/) | Workspace、DuckDuckGo、網頁抓取、Custom API、SQL 資料庫 |
| [嵌入其他 Bot](https://zhiro-labs.github.io/dango/advanced/embedding/) | 載入 Cog、用 `@discord_tool` 把指令包成 Agno 工具 |
| [Workflow 架構](https://zhiro-labs.github.io/dango/features/workflow/) | 四步驟 Agno pipeline 的內部運作方式 |
| [VPS 部署](https://zhiro-labs.github.io/dango/advanced/vps/) | 用 SSH 通道安全地在伺服器上運行 |

---

Built with [Agno](https://docs.agno.com) · [discord.py](https://discordpy.readthedocs.io)

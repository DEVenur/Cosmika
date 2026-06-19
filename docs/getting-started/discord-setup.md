---
summary: "Create a Discord bot, enable required intents, and generate an invite link."
---

# Discord Setup

Before running Dango, you need a Discord bot application with the right permissions. This takes about five minutes.

## 1. Create a Bot

Go to the [Discord Developer Portal](https://discord.com/developers/applications) and create a new application. In the **Bot** tab, click **Add Bot** and copy the **Bot Token** — you will need it during setup.

## 2. Enable Privileged Gateway Intents

Still in the **Bot** tab, scroll down to **Privileged Gateway Intents** and enable both:

| Intent | Why it's needed |
|---|---|
| **Server Members Intent** | Read user display names |
| **Message Content Intent** | Read message text |

## 3. Invite the Bot to Your Server

Go to **OAuth2 → URL Generator**. Under **Scopes**, select `bot` and `applications.commands`. Under **Bot Permissions**, select:

| Category | Permission |
|---|---|
| General | View Channels |
| Text | Send Messages |
| Text | Attach Files |
| Text | Read Message History |

Copy the generated URL, open it in your browser, and add the bot to your server.

## Next Steps

With your bot token ready, choose how to run Dango:

- [Docker Setup](docker.md) — recommended, no Python required
- [uv Setup](uv.md) — for developers or low-spec machines

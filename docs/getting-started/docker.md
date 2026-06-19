---
summary: "Recommended path — no Python required, configure from the browser."
description: "Install Dango Discord AI bot with Docker in minutes — no Python required. Pull the image, start with docker compose, and configure via the browser-based setup wizard."
tags:
  - Getting Started
  - Docker
  - Installation
---

# Docker Setup

The Docker path requires no Python installation. Everything runs in a container and you configure it through the browser.

## Prerequisites

- Docker ([Docker Desktop](https://www.docker.com/products/docker-desktop/) on Mac/Windows, [OrbStack](https://orbstack.dev) on Mac, or [Docker Engine](https://docs.docker.com/engine/install/) on Linux)
- A Discord bot token — see [Discord Setup](discord-setup.md)
- An API key for your chosen model provider

## Steps

### 1. Download `docker-compose.yml`

Navigate to the folder where you want to install Dango, then download the file:

```bash
curl -O https://raw.githubusercontent.com/zhiro-labs/dango/main/docker-compose.yml
```

### 2. Start the containers

```bash
docker compose up -d && docker compose logs -f
```

`-d` runs the containers in the background. `logs -f` streams output to your terminal — press **Ctrl+C** to stop watching; the containers keep running.

### 3. Open the setup wizard

Go to `http://localhost:17860` in your browser. The wizard will ask for:

- Discord Bot Token
- Model provider and API key
- Bot personality (system prompt)

Save, and the bot connects to Discord automatically.

### 4. Test the bot

In Discord, mention the bot in any channel it can see:

```
@YourBotName hello!
```

It should reply within a few seconds. If it doesn't, run `docker compose logs` to check for errors.

## Managing the bot

```bash
# Stop (preserves your data)
docker compose stop

# Start again
docker compose start

# Pull the latest image and restart
docker compose pull && docker compose up -d
```

Your data (`data/`, `config/`, `workspace/`) lives in a Docker volume and survives updates.

## Custom commands & tools

The `bot` service mounts a `./custom` folder next to your `docker-compose.yml`, so
you can add your own Discord commands and agent tools without rebuilding the image.
On first run the folder is seeded with `*.example` templates. To activate them:

```bash
cp custom/commands.py.example custom/commands.py   # edit it, then:
docker compose restart bot
```

See [Custom Commands & Tools](../features/extensions.md) for how to write them.

!!! note "Extra Python packages"
    If a custom tool needs a package that isn't in the image (e.g. the Google Drive
    provider needs `google-api-python-client`), the volume mount alone isn't enough —
    build a derived image:

    ```dockerfile
    FROM ghcr.io/zhiro-labs/dango:latest
    RUN uv add google-api-python-client google-auth-httplib2 google-auth-oauthlib
    ```

    then point the `bot` service at it with `build:` instead of `image:`. Custom tools
    that only use the standard library and existing dependencies work with the mount alone.

## Running on a VPS?

The web dashboard has no login screen — do not expose port 17860 to the internet. See [VPS Deployment](../advanced/vps.md) for the SSH tunnel approach.

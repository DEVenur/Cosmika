# Runtime Config

Runtime settings are stored in `config/runtime.yml` and managed through Discord slash commands. Changes take effect immediately — no restarts needed.

## What's in runtime.yml

```yaml
allowed_channels:   # channel IDs where the bot responds without a mention
  - 123456789012345678

allowed_users:      # user IDs allowed to DM the bot
  - 111222333444555666

timezone: UTC       # timezone for timestamps in the system prompt
discord_activity: Surfing   # bot's Discord activity status
```

The bot writes this file automatically when you use slash commands. You can also edit it by hand; the bot picks up changes on the next message.

## Slash Commands

All settings in `runtime.yml` are managed through Discord slash commands — no file editing needed. See the [Slash Commands reference](../usage/commands.md) for the full list.

## Default behaviour

Without any `/addchannel` setup, the bot only responds when directly mentioned (`@BotName`). Add channels to let it respond to all messages there.

DMs are blocked by default. Use `/adduser` to grant DM access per user.

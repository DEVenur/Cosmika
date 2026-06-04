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

All admin commands require the **Administrator** permission. Responses are ephemeral (only visible to you).

### Channel management

| Command | Description |
|---|---|
| `/addchannel` | Allow the bot to respond in the current channel without being mentioned |
| `/removechannel` | Remove the current channel from the allowed list |
| `/listchannels` | List all allowed channels in this server |

### User management (DMs)

| Command | Description |
|---|---|
| `/adduser @user` | Allow a user to DM the bot |
| `/removeuser @user` | Remove a user from the DM allowlist |
| `/listusers` | List all users allowed to DM the bot |

### Other settings

| Command | Description |
|---|---|
| `/sethistorylimit <n>` | Number of past messages included as context (e.g. `20`) |
| `/settimezone <tz>` | Bot's timezone for timestamps — supports autocomplete (e.g. `Asia/Taipei`) |
| `/setactivity <text>` | Discord activity status message (max 128 characters) |
| `/refreshmetadata` | Refresh display names for all saved channels and users |

## Default behaviour

Without any `/addchannel` setup, the bot only responds when directly mentioned (`@BotName`). Add channels to let it respond to all messages there.

DMs are blocked by default. Use `/adduser` to grant DM access per user.

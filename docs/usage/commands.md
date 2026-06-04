# Slash Commands

## Chat

Available to all users.

| Command | Description |
|---|---|
| `/newchat` | Drops a `[new chat]` marker in the channel. The bot ignores all history before this point. |
| `/deep <message>` | Send a message and force the deep model to respond. Requires `DEEP_MODEL` to be configured. Optionally accepts an image attachment. |

## Admin

Requires the **Administrator** server permission. All responses are ephemeral (only visible to you).

### Channels

| Command | Description |
|---|---|
| `/addchannel` | Allow the bot to respond to all messages in the current channel (not just mentions) |
| `/removechannel` | Remove the current channel from the allowed list |
| `/listchannels` | Show all allowed channels in this server |

### Users (DMs)

| Command | Description |
|---|---|
| `/adduser @user` | Allow a user to DM the bot directly |
| `/removeuser @user` | Remove a user from the DM allowlist |
| `/listusers` | Show all users allowed to DM the bot |

### Settings

| Command | Arguments | Description |
|---|---|---|
| `/sethistorylimit` | `<n>` | Number of past messages to include as context |
| `/settimezone` | `<tz>` | Timezone for timestamps injected into the system prompt. Supports autocomplete. |
| `/setactivity` | `<text>` | Bot's Discord activity status (max 128 characters). Persists across restarts. |
| `/refreshmetadata` | — | Refresh stored display names for all saved channels and users |

# Conversations

## Starting a conversation

| Method | How |
|---|---|
| **Mention** | `@BotName hello!` in any channel the bot can see |
| **Allowed channel** | Send a message normally — no mention needed if the channel is in the allowed list (set with `/addchannel`) |
| **Direct Message** | DM the bot directly (your user ID must be added first with `/adduser`) |

## Continuing a conversation

The bot fetches recent channel history automatically, so you can keep replying without mentioning it again. Use `/sethistorylimit` to control how far back it looks.

## Starting fresh

Run `/newchat` to drop a `[new chat]` marker. The bot ignores everything before that point and treats your next message as the start of a new conversation.

## Images

Attach an image to your message — the bot passes it straight to the model. Both direct messages and channel messages support image attachments.

## Reply context

When you reply to a Discord message (the native reply feature), the quoted message content is automatically included in the prompt. The bot sees who said what, formatted naturally.

## Forcing the deep model

Use `/deep <message>` to send a message that always goes to `DEEP_MODEL`, regardless of auto-routing. Useful when you know a question needs the more capable model.

## Mention resolution

`@user` and `@role` tokens in conversation history are replaced with real display names before the model sees them, so the model reads "Alice said..." instead of `<@123456789>`.

## Automatic behaviours

These happen without any commands:

| Behaviour | Notes |
|---|---|
| Table rendering | Markdown tables in replies are converted to PNG images |
| Long message splitting | Responses over 2000 characters are split across multiple messages |
| Google Search | Gemini models search the web when needed (`GEMINI_SEARCH=true` by default) |
| URL fetching | Gemini-native URL reading (`GEMINI_URL_CONTEXT=true`, opt-in) or any-provider URL reading (`ENABLE_WEBSITE_TOOLS=on`) |
| DuckDuckGo search | Any provider, opt-in (`ENABLE_DUCKDUCKGO=on`) |
| Auto-routing | Complex messages go to the deep model when `AUTO_ROUTE=on` |
| Context trimming | Oldest messages are dropped when history exceeds `CONTEXT_TOKEN_BUDGET` |
| Workspace access | Bot reads files from `WORKSPACE_ROOT` when `ENABLE_WORKSPACE=on` |

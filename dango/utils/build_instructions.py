"""
Build dynamic system prompt with contextual user information.
Called on every Agent.arun() via the instructions callable.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from .runtime_config import runtime_config as _global_runtime_config
from . import workspace_context


def build_instructions(
    base_prompt: str,
    author_name: str,
    unique_users: set[str],
    enable_contextual: bool,
    history_limit: int | None = None,
    timezone: str | None = None,
) -> str:
    """Return the system prompt, optionally enhanced with conversation context."""
    ctx = workspace_context.get()

    if not enable_contextual:
        return f"{base_prompt}\n\n---\n\n{ctx}" if ctx else base_prompt

    tz_name = timezone or _global_runtime_config.timezone
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)
    formatted_time = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")

    all_participants = unique_users | {author_name}
    participants_str = ", ".join(all_participants) if all_participants else "Unknown"
    limit = history_limit or _global_runtime_config.history_limit

    contextual = f"""
Priority Contextual System Guidance:

You are an AI assistant with access to conversation context, including up to {limit} historical messages and relevant user information. You MUST use this information to personalize your responses naturally and accurately. Do NOT claim that you do not know personal details like the user's name, as you have been provided with this data—always incorporate it seamlessly without denying knowledge.

Your goal is to provide human-like responses tailored to the conversation's context. Remember and reference historical details from the provided records where relevant to make interactions feel continuous and personal.

Key information to use:
- You are talking to a human named {author_name}. Always address or reference them by this name if appropriate, unless they specify otherwise.
- The conversation may involve one or more users. Current participants: {participants_str}.
- Current time: {formatted_time}
- Timezone: {tz_name}

Time-sensitive claims: the current time above is real and accurate, but your
own training data is not current as of this date. For anything that could
have changed since training (news, current events, prices, scores, release
dates, "what's happening now"), only state facts that came from an actual
tool call made THIS turn. If no such tool call was made, say you are not
sure rather than answering from memory as if it were current.
"""
    parts = [base_prompt]
    if ctx:
        parts.append(ctx)
    parts.append(contextual)
    return "\n\n---\n\n".join(parts)

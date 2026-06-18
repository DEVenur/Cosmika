"""Normalized call context shared by Discord commands and Agent tools.

A custom function may declare ``ctx`` as its first parameter to receive a
:class:`Ctx` regardless of whether it was invoked as a Discord slash command
or by the agent during a chat turn.

For the agent path the context is carried out-of-band through a ContextVar
that the agent runner sets right before ``agent.arun()``. This deliberately
does not rely on Agno injecting ``session_state`` into the tool signature, so
the LLM-facing tool schema stays clean (only the user's own parameters) and
the mechanism is independent of Agno internals.
"""

from contextvars import ContextVar, Token
from dataclasses import dataclass, field
from typing import Any, Optional

# Per-request session_state, set by the agent runner around agent.arun().
# ContextVars set before an await are visible to all descendant coroutines and
# tasks spawned during that run, so tools invoked by the LLM can read it.
_request_ctx: ContextVar[Optional[dict]] = ContextVar("dango_request_ctx", default=None)


def set_request_context(session_state: Optional[dict]) -> Token:
    """Store per-request session_state. Pass the returned token to
    :func:`reset_request_context` in a ``finally`` block."""
    return _request_ctx.set(session_state)


def reset_request_context(token: Token) -> None:
    _request_ctx.reset(token)


@dataclass
class Ctx:
    """Where a custom function was invoked from, normalized across both paths."""

    source: str  # "discord_command" | "agent"
    author_name: str = "User"
    author_id: Optional[int] = None
    channel_id: Optional[int] = None
    channel_name: str = ""
    guild_id: Optional[int] = None
    guild_name: str = ""
    # Precise IDs of members/roles the triggering message tagged. Empty on the
    # command path (slash commands carry no message mentions).
    mentioned_user_ids: list[int] = field(default_factory=list)
    mentioned_role_ids: list[int] = field(default_factory=list)
    # Discord permission names the author holds in the guild (e.g.
    # "manage_guild"), so tools can gate privileged actions. Empty in DMs.
    author_permissions: list[str] = field(default_factory=list)
    # discord.Interaction when source == "discord_command", else None.
    interaction: Any = None
    # discord.ext.commands.Bot when available (command path), else None.
    bot: Any = None

    @classmethod
    def from_agent(cls) -> "Ctx":
        """Build a Ctx for an agent (LLM) invocation from the request ContextVar."""
        ss = _request_ctx.get() or {}
        return cls(
            source="agent",
            author_name=ss.get("author_name", "User"),
            author_id=ss.get("author_id"),
            channel_id=ss.get("channel_id"),
            channel_name=ss.get("channel_name", "") or "",
            guild_id=ss.get("guild_id"),
            guild_name=ss.get("guild_name", "") or "",
            mentioned_user_ids=[u["id"] for u in ss.get("mentioned_users", [])],
            mentioned_role_ids=[r["id"] for r in ss.get("mentioned_roles", [])],
            author_permissions=list(ss.get("author_permissions", [])),
        )

    @classmethod
    def from_interaction(cls, interaction: Any, bot: Any = None) -> "Ctx":
        """Build a Ctx from a Discord slash-command interaction."""
        channel = getattr(interaction, "channel", None)
        guild = getattr(interaction, "guild", None)
        user = getattr(interaction, "user", None)
        # user is a Member inside a guild (carries guild_permissions), a plain
        # User in DMs (no permissions).
        perms = getattr(user, "guild_permissions", None)
        author_permissions = [name for name, value in perms if value] if perms else []
        return cls(
            source="discord_command",
            author_name=getattr(user, "display_name", None) or "User",
            author_id=getattr(user, "id", None),
            channel_id=getattr(channel, "id", None),
            channel_name=getattr(channel, "name", "") or "",
            guild_id=getattr(guild, "id", None),
            guild_name=getattr(guild, "name", "") or "",
            author_permissions=author_permissions,
            interaction=interaction,
            bot=bot or getattr(interaction, "client", None),
        )

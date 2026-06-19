"""Registry and decorators for user-defined commands and agent tools.

Developers drop ``.py`` files into the ``custom/`` directory (gitignored) and
decorate their functions with one of:

    @command           -> a Discord slash command only
    @agent_tool        -> an Agent tool only (callable by the LLM)
    @command_and_tool  -> both at once (one function, two entry points)

The decorators only record a spec here. The loader (``loader.py``) turns these
specs into real Discord slash commands and Agno tools at startup. Whether the
agent may call a function is decided purely by which decorator is used — there
is no global switch, so exposure is always an explicit per-function opt-in.
"""

from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class ExtensionSpec:
    """One registered custom function and how it should be exposed."""

    fn: Callable
    name: str
    description: str
    expose_command: bool
    expose_tool: bool


# Populated at import time, when the loader imports each custom/*.py file.
_REGISTRY: list[ExtensionSpec] = []

# Raw Agno tools/toolkits/context-provider tools registered via register_tools().
_RAW_TOOLS: list = []


def _first_doc_line(fn: Callable) -> str:
    doc = (fn.__doc__ or "").strip()
    return doc.split("\n", 1)[0].strip() if doc else ""


def _register(
    fn: Callable,
    name: Optional[str],
    description: str,
    *,
    expose_command: bool,
    expose_tool: bool,
) -> Callable:
    _REGISTRY.append(
        ExtensionSpec(
            fn=fn,
            name=name or fn.__name__,
            description=description or _first_doc_line(fn),
            expose_command=expose_command,
            expose_tool=expose_tool,
        )
    )
    return fn


def _make_decorator(*, expose_command: bool, expose_tool: bool):
    """Build a decorator that supports @deco, @deco("name") and @deco(name=..., description=...)."""

    def decorator(name=None, description: str = ""):
        # Bare usage: @command applied directly to a function.
        if callable(name):
            return _register(
                name, None, "", expose_command=expose_command, expose_tool=expose_tool
            )

        def wrap(fn: Callable) -> Callable:
            return _register(
                fn, name, description, expose_command=expose_command, expose_tool=expose_tool
            )

        return wrap

    return decorator


command = _make_decorator(expose_command=True, expose_tool=False)
"""Register a Discord slash command. Not exposed to the agent."""

agent_tool = _make_decorator(expose_command=False, expose_tool=True)
"""Register an Agent tool the LLM can call. No Discord slash command."""

command_and_tool = _make_decorator(expose_command=True, expose_tool=True)
"""Register a function as BOTH a Discord slash command and an Agent tool."""


def register_tools(*tools) -> None:
    """Attach raw Agno tools/toolkits/context providers to the agent.

    For anything that is not a single decorated function — an Agno ``Toolkit``
    instance, or the list produced by a context provider's ``get_tools()`` — call
    this from a ``custom/*.py`` file so it reaches the agent without editing core
    code. Accepts plain functions, ``@tool`` functions, Toolkit instances, or
    lists/tuples of any of these::

        from dango.extensions import register_tools
        from agno.context.gdrive import GoogleDriveContextProvider

        register_tools(*GoogleDriveContextProvider().get_tools())

    These are exposed to the agent only; they are never turned into Discord slash
    commands.
    """
    for t in tools:
        if isinstance(t, (list, tuple)):
            _RAW_TOOLS.extend(t)
        else:
            _RAW_TOOLS.append(t)


def command_specs() -> list[ExtensionSpec]:
    return [s for s in _REGISTRY if s.expose_command]


def tool_specs() -> list[ExtensionSpec]:
    return [s for s in _REGISTRY if s.expose_tool]


def raw_tools() -> list:
    return list(_RAW_TOOLS)


def clear_registry() -> None:
    """Reset the registry. Used by tests and (later) hot-reload."""
    _REGISTRY.clear()
    _RAW_TOOLS.clear()

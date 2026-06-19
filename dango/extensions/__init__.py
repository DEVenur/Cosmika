"""Public SDK for user-defined Dango extensions.

Import these in your ``custom/*.py`` files::

    from dango.extensions import command, agent_tool, command_and_tool, Ctx

See ``custom/commands.py.example`` and ``custom/tools.py.example`` for usage.
"""

from .context import Ctx
from .loader import get_custom_tools, load_custom_modules, register_custom_commands
from .registry import agent_tool, command, command_and_tool, register_tools

__all__ = [
    # Decorators (used in custom/*.py)
    "command",
    "agent_tool",
    "command_and_tool",
    # Attach raw Agno toolkits / context providers (used in custom/*.py)
    "register_tools",
    # Call context
    "Ctx",
    # Loader (used by the app at startup)
    "load_custom_modules",
    "get_custom_tools",
    "register_custom_commands",
]

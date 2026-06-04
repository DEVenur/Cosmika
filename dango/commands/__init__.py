"""Discord slash commands module"""

from .admin_commands import AdminCog
from .chat_commands import ChatCog

__all__ = ["AdminCog", "ChatCog"]

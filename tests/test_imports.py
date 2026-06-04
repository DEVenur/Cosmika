"""
Tests to verify all modules can be imported successfully.
"""


def test_import_steps():
    """Test that all step modules can be imported."""
    from dango.steps import (
        call_discord_agent,
        extract_and_render_tables,
        fetch_and_process_history,
        send_discord_response,
    )

    assert fetch_and_process_history is not None
    assert call_discord_agent is not None
    assert extract_and_render_tables is not None
    assert send_discord_response is not None


def test_import_utils():
    """Test that all utility modules can be imported."""
    from dango.utils import (
        check_font_exists,
        env_onoff_to_bool,
    )

    assert check_font_exists is not None
    assert env_onoff_to_bool is not None


def test_import_build_instructions():
    """Test that build_instructions utility can be imported."""
    from dango.utils.build_instructions import build_instructions

    assert build_instructions is not None


def test_import_workflow():
    """Test that workflow module can be imported."""
    from dango.workflow import create_discord_workflow

    assert create_discord_workflow is not None


def test_import_commands():
    """Test that command Cogs can be imported and are proper Cog subclasses."""
    from discord.ext import commands

    from dango.commands import AdminCog, ChatCog

    assert issubclass(ChatCog, commands.Cog)
    assert issubclass(AdminCog, commands.Cog)


def test_chat_cog_has_listener():
    """Test that ChatCog registers on_message as a Cog listener."""
    from dango.commands import ChatCog

    listeners = [m for m in ChatCog.__cog_listeners__ if m[0] == "on_message"]
    assert len(listeners) == 1


def test_cog_app_commands():
    """Test that ChatCog and AdminCog declare expected app commands."""
    from dango.commands import AdminCog, ChatCog

    chat_cmd_names = {cmd.name for cmd in ChatCog.__cog_app_commands__}
    assert "newchat" in chat_cmd_names
    assert "deep" in chat_cmd_names

    admin_cmd_names = {cmd.name for cmd in AdminCog.__cog_app_commands__}
    expected = {"addchannel", "removechannel", "listchannels", "adduser", "removeuser",
                "listusers", "refreshmetadata", "sethistorylimit", "setactivity", "settimezone"}
    assert expected == admin_cmd_names

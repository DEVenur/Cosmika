"""
Tests for utility functions.
"""

from dango.utils import (
    check_font_exists,
    env_onoff_to_bool,
)


class TestConfigUtils:
    """Tests for config_utils module."""

    def test_env_onoff_to_bool_on(self):
        """Test env_onoff_to_bool with 'on' value."""
        assert env_onoff_to_bool("on") is True
        assert env_onoff_to_bool("ON") is True

    def test_env_onoff_to_bool_off(self):
        """Test env_onoff_to_bool with 'off' value."""
        assert env_onoff_to_bool("off") is False
        assert env_onoff_to_bool("OFF") is False

    def test_env_onoff_to_bool_invalid(self):
        """Test env_onoff_to_bool with invalid value."""
        assert env_onoff_to_bool("invalid") is False
        assert env_onoff_to_bool("") is False
        assert env_onoff_to_bool(None) is False



class TestDownloadFont:
    """Tests for download_font module."""

    def test_check_font_exists_returns_bool(self):
        """Test check_font_exists returns a boolean value."""
        result = check_font_exists()
        assert isinstance(result, bool)

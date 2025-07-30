"""Tests for version-related functionality."""

from cli_mcpx import __version__
from cli_mcpx.cli import app, create_version_message


class TestVersion:
    """Test version functionality."""

    def test_version_string(self):
        """Test that version string is properly set."""
        assert __version__ is not None
        assert isinstance(__version__, str)
        # In development, version should be "dev"
        assert __version__ == "dev" or "." in __version__

    def test_create_version_message(self):
        """Test version message creation."""
        test_version = "1.0.0"
        message = create_version_message(test_version)
        assert message == "cli-mcpx version: 1.0.0"

    def test_version_option(self, runner):
        """Test --version option."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "cli-mcpx version:" in result.stdout
        assert __version__ in result.stdout

    def test_version_short_option(self, runner):
        """Test -v short option."""
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert "cli-mcpx version:" in result.stdout

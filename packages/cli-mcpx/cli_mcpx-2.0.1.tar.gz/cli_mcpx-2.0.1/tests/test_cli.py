"""Tests for main CLI functionality."""

import pytest

from cli_mcpx.cli import app, display_message, exit_program


class TestCLI:
    """Test main CLI functionality."""

    def test_cli_without_arguments(self, runner):
        """Test CLI without any arguments."""
        result = runner.invoke(app, [])
        assert result.exit_code == 0

    def test_display_message(self, capsys):
        """Test display_message function."""

        def test_creator(value: str) -> str:
            return f"Test: {value}"

        display_message(test_creator, "hello")
        captured = capsys.readouterr()
        assert captured.out == "Test: hello\n"

    def test_exit_program(self):
        """Test exit_program function."""
        with pytest.raises(SystemExit) as exc_info:
            exit_program(0)
        assert exc_info.value.code == 0

        with pytest.raises(SystemExit) as exc_info:
            exit_program(1)
        assert exc_info.value.code == 1

    def test_main_callback(self, runner):
        """Test main callback function."""
        # This test ensures the main callback is covered
        result = runner.invoke(app, [])
        assert result.exit_code == 0

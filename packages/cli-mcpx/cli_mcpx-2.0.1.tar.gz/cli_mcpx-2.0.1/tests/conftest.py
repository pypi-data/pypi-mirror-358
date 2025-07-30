"""Pytest configuration and shared fixtures."""

import pytest
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Provide a CliRunner instance for testing CLI commands."""
    return CliRunner()

"""Tests for __init__ module."""

import sys
from unittest.mock import patch


class TestInit:
    """Test __init__ module functionality."""

    def test_version_fallback(self):
        """Test version fallback when package is not installed."""
        # Mock importlib.metadata.version to raise an exception
        with patch("importlib.metadata.version") as mock_version:
            mock_version.side_effect = Exception("Package not found")

            # Remove the module from sys.modules to force reimport
            if "cli_mcpx" in sys.modules:
                del sys.modules["cli_mcpx"]

            # Import the module
            import cli_mcpx

            # Check that version falls back to "dev"
            assert cli_mcpx.__version__ == "dev"

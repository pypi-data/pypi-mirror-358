"""cli-mcpx: A modern Python CLI tool for MCP (Model Context Protocol) server management."""

try:
    from importlib.metadata import version

    __version__ = version("cli-mcpx")
except Exception:
    __version__ = "dev"

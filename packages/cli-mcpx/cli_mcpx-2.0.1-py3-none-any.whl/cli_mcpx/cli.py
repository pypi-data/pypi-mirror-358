"""CLI entry point for cli-mcpx."""

import sys
from collections.abc import Callable
from functools import partial
from typing import Annotated

import typer

from cli_mcpx import __version__


def create_version_message(version: str) -> str:
    """
    Create version message string.

    Pure function that formats the version message.
    """
    return f"cli-mcpx version: {version}"


def display_message(message_creator: Callable[[str], str], version: str) -> None:
    """
    Display message using the provided message creator function.

    Higher-order function that accepts a message creator function.
    """
    typer.echo(message_creator(version))


def exit_program(code: int = 0) -> None:
    """Exit the program with the given code."""
    sys.exit(code)


def version_callback(value: bool) -> None:
    """
    Handle version option callback.

    Functional composition of display and exit operations.
    """
    if value:
        # Compose functions using partial application
        display_version = partial(display_message, create_version_message)
        display_version(__version__)
        exit_program()


# Create the main Typer app
app = typer.Typer(
    name="cli-mcpx",
    help="A modern Python CLI tool for MCP (Model Context Protocol) server management",
    no_args_is_help=True,
    add_completion=True,
)


# Version option using functional approach
version_option = partial(
    typer.Option,
    "--version",
    "-v",
    callback=version_callback,
    is_eager=True,
    help="Show the version and exit",
)


@app.callback()
def main(
    ctx: typer.Context,
    version: Annotated[bool | None, version_option()] = None,
) -> None:
    """
    A modern Python CLI tool for MCP (Model Context Protocol) server management.

    Use --help to see available commands and options.
    Use --install-completion to set up shell auto-completion.
    """
    pass  # Version is handled by the callback if provided


if __name__ == "__main__":
    app()

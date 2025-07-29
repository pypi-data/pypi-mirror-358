# ruff: noqa: B008

import logging

from typer import Typer

from dear_assistant import __version__

cli_app = Typer(name=f"Dear Assistant [{__version__}]")


@cli_app.command()
def main() -> None:
    """Build the database."""
    print("I am still in developement. But hello!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cli_app()

"""Jivas Package Repository CLI tool."""

import click

from jvcli import __version__
from jvcli.commands.auth import login, logout, signup
from jvcli.commands.clean import clean
from jvcli.commands.client import client
from jvcli.commands.create import create
from jvcli.commands.download import download
from jvcli.commands.info import info
from jvcli.commands.publish import publish
from jvcli.commands.server import server
from jvcli.commands.startproject import startproject
from jvcli.commands.studio import studio
from jvcli.commands.update import update


@click.group()
@click.version_option(__version__, prog_name="jvcli")
def jvcli() -> None:
    """Jivas Package Repository CLI tool."""
    pass  # pragma: no cover


# Register command groups
jvcli.add_command(create)
jvcli.add_command(update)
jvcli.add_command(download)
jvcli.add_command(publish)
jvcli.add_command(info)
jvcli.add_command(studio)
jvcli.add_command(client)
jvcli.add_command(startproject)
jvcli.add_command(clean)
jvcli.add_command(server)

# Register standalone commands
jvcli.add_command(signup)
jvcli.add_command(login)
jvcli.add_command(logout)

if __name__ == "__main__":
    jvcli()  # pragma: no cover

"""Command line interface entry point for Glacium."""

import click

# Einzel-Commands importieren
from .new import cli_new
from .run import cli_run   # sobald du run.py gebaut hast
from .list import cli_list
from .projects import cli_projects
from .select   import cli_select
from .job      import cli_job
from .sync import cli_sync
from .remove import cli_remove

@click.group()
def cli():
    """Glacium – project & job control."""
    pass

# Befehle registrieren
cli.add_command(cli_new)
cli.add_command(cli_run)
cli.add_command(cli_list)
cli.add_command(cli_projects)
cli.add_command(cli_select)
cli.add_command(cli_job)
cli.add_command(cli_sync)
cli.add_command(cli_remove)

# entry-point für `python -m glacium.cli`
if __name__ == "__main__":
    cli()


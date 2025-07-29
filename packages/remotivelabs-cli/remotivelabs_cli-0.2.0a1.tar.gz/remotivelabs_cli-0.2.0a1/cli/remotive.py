from __future__ import annotations

import os
from importlib.metadata import version

import typer
from rich import print as rich_print
from rich.console import Console
from trogon import Trogon  # type: ignore
from typer.main import get_group

from cli.broker.brokers import app as broker_app
from cli.cloud.cloud_cli import app as cloud_app
from cli.connect.connect import app as connect_app
from cli.settings import settings
from cli.settings.migrate_all_token_files import migrate_any_legacy_tokens
from cli.tools.tools import app as tools_app
from cli.topology.cmd import app as topology_app
from cli.typer import typer_utils

err_console = Console(stderr=True)

if os.getenv("GRPC_VERBOSITY") is None:
    os.environ["GRPC_VERBOSITY"] = "NONE"

app = typer_utils.create_typer(
    rich_markup_mode="rich",
    help="""
Welcome to RemotiveLabs CLI - Simplify and automate tasks for cloud resources and brokers

For documentation - https://docs.remotivelabs.com
""",
)

# settings.set_default_config_as_env()


def version_callback(value: bool) -> None:
    if value:
        my_version = version("remotivelabs-cli")
        typer.echo(my_version)
        raise typer.Exit()


def test_callback(value: int) -> None:
    if value:
        rich_print(value)
        raise typer.Exit()


def _migrate_old_tokens() -> None:
    tokens = settings.list_personal_tokens()
    tokens.extend(settings.list_service_account_tokens())
    if migrate_any_legacy_tokens(tokens):
        err_console.print("Migrated old credentials and configuration files, you may need to login again or activate correct credentials")


def _set_default_org_as_env() -> None:
    """
    If not already set, take the default organisation from file and set as env
    This has to be done early before it is read
    """
    if "REMOTIVE_CLOUD_ORGANIZATION" not in os.environ:
        org = settings.get_cli_config().get_active_default_organisation()
        if org is not None:
            os.environ["REMOTIVE_CLOUD_ORGANIZATION"] = org


@app.callback()
def main(
    _the_version: bool = typer.Option(None, "--version", callback=version_callback, is_eager=False, help="Print current version"),
) -> None:
    _set_default_org_as_env()
    _migrate_old_tokens()
    # Do other global stuff, handle other global options here


@app.command()
def tui(ctx: typer.Context) -> None:
    """
    Explore remotive-cli and generate commands with this textual user interface application
    """

    Trogon(get_group(app), click_context=ctx).run()


app.add_typer(broker_app, name="broker", help="Manage a single broker - local or cloud")
app.add_typer(
    cloud_app,
    name="cloud",
    help="Manage resources in RemotiveCloud",
)
app.add_typer(
    topology_app,
    name="topology",
    help="""
RemotiveTopology actions

Read more at https://docs.remotivelabs.com/docs/remotive-topology
""",
)
app.add_typer(connect_app, name="connect", help="Integrations with other systems")
app.add_typer(tools_app, name="tools")

import re
from typing import Dict, Optional

import click
from dotenv import dotenv_values, set_key

from tinybird.tb.client import TinyB
from tinybird.tb.modules.cli import cli
from tinybird.tb.modules.common import echo_safe_humanfriendly_tables_format_smart_table
from tinybird.tb.modules.feedback_manager import FeedbackManager
from tinybird.tb.modules.project import Project


@cli.group()
@click.pass_context
def secret(ctx):
    """Secret commands."""


@secret.command(name="ls")
@click.option("--match", default=None, help="Retrieve any secrets matching the pattern. For example, --match _test")
@click.pass_context
def secret_ls(ctx: click.Context, match: Optional[str]):
    """List secrets"""

    client: TinyB = ctx.ensure_object(dict)["client"]
    secrets = client.secrets()
    columns = ["name", "created_at", "updated_at"]
    table_human_readable = []
    table_machine_readable = []
    pattern = re.compile(match) if match else None

    for secret in secrets:
        name = secret["name"]

        if pattern and not pattern.search(name):
            continue

        created_at = secret["created_at"]
        updated_at = secret["updated_at"]

        table_human_readable.append((name, created_at, updated_at))
        table_machine_readable.append({"name": name, "created at": created_at, "updated at": updated_at})

    click.echo(FeedbackManager.info(message="** Secrets:"))
    echo_safe_humanfriendly_tables_format_smart_table(table_human_readable, column_names=columns)
    click.echo("\n")


@secret.command(name="set")
@click.argument("name")
@click.argument("value", required=False)
@click.option("--multiline", is_flag=True, help="Whether to use multiline input")
@click.pass_context
def secret_set(ctx: click.Context, name: str, value: Optional[str], multiline: bool):
    """Create or update secrets"""
    try:
        if not value:
            if multiline:
                value = click.edit(
                    "🔗 IMPORTANT: THIS LINE MUST BE DELETED. Enter your secret value:", extension=".txt"
                )
            else:
                value = click.prompt("Enter value", hide_input=True)

        assert isinstance(value, str)

        click.echo(FeedbackManager.highlight(message=f"\n» Setting secret '{name}'..."))

        client: TinyB = ctx.ensure_object(dict)["client"]
        existing_secret = None
        try:
            existing_secret = client.get_secret(name)
        except Exception:
            pass

        if existing_secret:
            client.update_secret(name, value)
        else:
            client.create_secret(name, value)
        click.echo(FeedbackManager.success(message=f"\n✓ Secret '{name}' set"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))


@secret.command(name="rm")
@click.argument("name")
@click.pass_context
def secret_rm(ctx: click.Context, name: str):
    """Delete a secret"""
    try:
        click.echo(FeedbackManager.highlight(message=f"\n» Deleting secret '{name}'..."))
        client: TinyB = ctx.ensure_object(dict)["client"]
        client.delete_secret(name)
        click.echo(FeedbackManager.success(message=f"\n✓ Secret '{name}' deleted"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))


def load_secrets(project: Project, client: TinyB):
    try:
        env_vars: Dict[str, str] = {}

        # Load secrets from .env file
        env_file = ".env"
        env_path = project.path / env_file

        if env_path.exists():
            env_values = dotenv_values(env_path)
            if env_values:
                env_vars.update({k: v for k, v in env_values.items() if v is not None})

        # Load secrets from .env.local file
        env_file = ".env.local"
        env_path = project.path / env_file

        if env_path.exists():
            env_values = dotenv_values(env_path)
            if env_values:
                env_vars.update({k: v for k, v in env_values.items() if v is not None})

        if len(env_vars.keys()) == 0:
            return

        click.echo(FeedbackManager.highlight(message="\n» Loading secrets from .env files..."))

        for name, value in env_vars.items():
            if not value:
                continue

            try:
                existing_secret = client.get_secret(name)
            except Exception:
                existing_secret = None
            try:
                if existing_secret:
                    client.update_secret(name, value)
                else:
                    client.create_secret(name, value)
            except Exception as e:
                click.echo(FeedbackManager.error(message=f"✗ Error setting secret '{name}': {e}"))

        click.echo(FeedbackManager.success(message="✓ Secrets loaded!"))
    except Exception as e:
        click.echo(FeedbackManager.error(message=f"✗ Error: {e}"))


def save_secret_to_env_file(project: Project, name: str, value: str):
    env_path = project.path / ".env.local"

    if not env_path.exists():
        env_path.touch()

    set_key(env_path, key_to_set=name, value_to_set=value)

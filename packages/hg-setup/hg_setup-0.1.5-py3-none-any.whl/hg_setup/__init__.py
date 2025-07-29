"""hg-setup package"""

import sys

import rich_click as click

from .init_cmd import init_tui, init_auto
from .hgrcs import check_hg_conf_file, read_hg_conf_simple
from .completion import init_shell_completions, init_shell_completion_1_shell


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def main():
    """Setup Mercurial and modify its configuration files"""


@main.command(context_settings=CONTEXT_SETTINGS)
@click.option("-n", "--name", help="user name", default=None)
@click.option("-e", "--email", help="email address", default=None)
@click.option("--auto", is_flag=True, help="no user interaction")
@click.option(
    "-f", "--force", is_flag=True, help="Act even if a config file already exists"
)
def init(name, email, auto, force):
    """Initialize Mercurial configuration file"""
    init_shell_completions()
    exists, path_config = check_hg_conf_file()
    if exists:
        if not force:
            click.echo(
                f"File {path_config} already exists. Nothing to do.\n"
                "Run `hg-setup init -f` to launch the user interface."
            )
            return

        name_hgrc, email_hgrc, editor = read_hg_conf_simple(path_config)

        if name is None and name_hgrc is not None:
            name = name_hgrc
        if email is None and email_hgrc is not None:
            email = email_hgrc
    else:
        editor = None

    if auto:
        init_auto(name, email, editor, force, path_config)
    else:
        init_tui(name, email, editor)


# @main.command(context_settings=CONTEXT_SETTINGS)
# @click.option("-l", "--local", is_flag=True, help="edit repository config")
# def config(local):
#     """UI to edit Mercurial configuration files"""

#     click.echo("Not implemented")
#     click.echo(f"{local = }")


@main.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.option("--share-dir", help="share dir", default=None)
def init_shell_completion(name, share_dir):
    """init shell completion for a specific shell

    Examples:

      hg-setup init-shell-completion bash

      hg-setup init-shell-completion zsh

    """
    supported_shells = ["bash", "zsh"]
    if name not in supported_shells:
        str_shells = ". ".join(supported_shells)
        click.echo(f"'{name}' not in supported shells ({str_shells}).")
        sys.exit(1)
    init_shell_completion_1_shell(name, share_dir)

"""Shell completion

bash
----

Mercurial bash completion file (called `hg`) can be in:

- /etc/bash_completion.d
- /usr/share/bash-completion/completions
- ~/.local/share/bash-completion/completions

zsh
---

Mercurial zsh completion file (called `_hg`) can be in:

- /usr/share/zsh/site-functions
- /usr/share/zsh/*/functions
- ~/.local/share/zsh/site-functions
- ~/.zfunc
- $ZSH_CUSTOM/plugins/hg

tcsh
----

???

Powershell
----------

???

fish
----

- ~/.config/fish/completions

elvish
------

???

xonsh
-----

Use bash completion + other stuff.

"""

import os

from importlib import resources
from pathlib import Path
from shutil import which

import rich_click as click

shells = ["bash", "zsh"]

# for testing
CONSIDER_SYSTEM_PATHS = True


def detect_available_shells():
    return [shell for shell in shells if which(shell) is not None]


def detect_completion_1_shell(name, dirs):
    for path_dir in dirs:
        path_dir = Path(path_dir)
        if not path_dir.exists():
            continue
        if (path_dir / name).exists():
            return True
    return False


def detect_shells_with_completion():
    dirs_completion = {
        "bash": [
            Path.home() / ".local/share/bash-completion/completions",
        ],
        "zsh": [
            Path.home() / ".local/share/zsh/site-functions",
        ],
    }

    if CONSIDER_SYSTEM_PATHS:
        dirs_completion["bash"].extend(
            [
                "/etc/bash_completion.d",
                "/usr/share/bash-completion/completions",
            ]
        )
        dirs_completion["zsh"].append("/usr/share/zsh/site-functions")

    name_completion = {"bash": "hg", "zsh": "_hg"}
    results = []
    for shell in shells:
        name = name_completion[shell]
        if detect_completion_1_shell(name, dirs_completion[shell]):
            results.append(shell)
    return set(results)


def init_shell_completion_1_shell(name, share_dir=None):
    if share_dir is None:
        try:
            share_dir = Path(os.environ["XDG_DATA_HOME"])
        except KeyError:
            share_dir = Path.home() / ".local/share"

    match name:
        case "bash":
            path_dest = share_dir / "bash-completion/completions/hg"
        case "zsh":
            path_dest = share_dir / "zsh/site-functions/_hg"
        case _:
            assert False

    if path_dest.exists():
        click.echo(f"{path_dest} already exists")
        return

    text = resources.files("hg_setup.data").joinpath(f"{name}_completion").read_text()
    path_dest.parent.mkdir(parents=True, exist_ok=True)
    path_dest.write_text(text)
    click.echo(f"{path_dest} written")


def init_shell_completions():
    if os.name == "nt":
        return
    shell_ok = detect_shells_with_completion()
    for shell in detect_available_shells():
        if shell in shell_ok:
            continue
        init_shell_completion_1_shell(shell)

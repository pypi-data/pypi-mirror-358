"""hg-setup init"""

import os

from datetime import datetime
from shutil import which

from textual.app import App, ComposeResult, Screen
from textual import on, work
from textual.containers import Horizontal, VerticalScroll, Center
from textual.widgets import (
    Button,
    Label,
    Log,
    Input,
    Header,
    Footer,
    Checkbox,
    Markdown,
)

import rich_click as click

from textual.binding import Binding

from .hgrcs import HgrcCodeMaker, check_hg_conf_file, name_default

editors_possible = ["nano", "notepad", "emacs", "vim", "vi"]
editors_avail = [editor for editor in editors_possible if which(editor) is not None]
try:
    editor_default = editors_avail[0]
except IndexError:
    editor_default = ""

inputs = {
    "name": dict(placeholder="Firstname Lastname"),
    "email": dict(placeholder="Email"),
    "editor": dict(value=editor_default),
}

checkboxs = {
    "tweakdefaults": True,
    "simple history edition": True,
    "advanced history edition": False,
}


class QuestionScreen(Screen[bool]):
    """Screen with a parameter."""

    def __init__(self, question: str) -> None:
        self.question = question
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.question)
        yield Button("Yes", id="yes", variant="success")
        yield Button("No", id="no")

    @on(Button.Pressed, "#yes")
    def handle_yes(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#no")
    def handle_no(self) -> None:
        self.dismiss(False)


class Frame(VerticalScroll):
    pass


class VerticalHgrcParams(Frame):
    inputs: dict
    checkboxs: dict

    def compose(self) -> ComposeResult:
        self.inputs = {key: Input(**kwargs) for key, kwargs in inputs.items()}
        self.checkboxs = {
            key.replace(" ", "_"): Checkbox(key, value=value)
            for key, value in checkboxs.items()
        }

        yield Label("[b]Name and email?[/b]")
        for key in ["name", "email"]:
            yield self.inputs[key]

        question_editor = "[b]Your preferred editor?[/b]"
        if "emacs" in editors_avail:
            question_editor += ' (could be "emacs -nw -Q")'
        yield Label(question_editor)
        yield self.inputs["editor"]

        yield Label("[b]Get improvements to the UI over time?[/b] (recommended)")
        yield self.checkboxs["tweakdefaults"]

        yield Label("[b]What about history edition?[/b]")
        for key in tuple(self.checkboxs.keys())[1:]:
            yield self.checkboxs[key]


class InitHgrcApp(App):
    _hgrc_text: str
    log_hgrc: Markdown
    _label_feedback: Label
    vert_hgrc_params: VerticalHgrcParams
    _button_save: Button

    CSS_PATH = "init_app.tcss"

    BINDINGS = [
        Binding(key="q", action="quit", description="Quit the app"),
        Binding(
            key="s",
            action="save_hgrc",
            description="Save config file",
        ),
    ]

    def __init__(self, name, email, editor):
        if name is not None:
            inputs["name"]["value"] = name
        if email is not None:
            inputs["email"]["value"] = email
        if editor is not None:
            inputs["editor"]["value"] = editor

        self.hgrc_maker = HgrcCodeMaker()
        super().__init__()

    def _create_hgrc_code(self):
        kwargs = {key: inp.value for key, inp in self.vert_hgrc_params.inputs.items()}
        kwargs.update(
            {
                key: checkbox.value
                for key, checkbox in self.vert_hgrc_params.checkboxs.items()
            }
        )
        self._hgrc_text = self.hgrc_maker.make_text(**kwargs)
        return self._hgrc_text

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal():
            with VerticalScroll():
                self.vert_hgrc_params = VerticalHgrcParams()
                yield self.vert_hgrc_params

            with VerticalScroll():
                self.log_hgrc = Log("", auto_scroll=False)
                yield self.log_hgrc
                self._button_save = Button.success(
                    "Save user config file", id="button_save"
                )
                with Center():
                    yield self._button_save

        yield Footer()

    def on_mount(self) -> None:
        self.title = f"Initialize Mercurial user configuration file (~/{name_default})"

        widget = self.log_hgrc
        # widget.styles.height = "8fr"
        widget.border_title = "Read resulting config text (press on 's' to save)"

        widget = self._button_save
        widget.styles.height = "3"

        widget = self.vert_hgrc_params
        widget.styles.height = "2fr"
        widget.border_title = "Enter few parameters"

    @work
    async def action_save_hgrc(self) -> None:
        """Save new ~/.hgrc"""
        exists, path_hgrc = check_hg_conf_file()
        if exists:
            if await self.push_screen_wait(
                QuestionScreen(
                    "A user config file already exists. Do you want to replace it?"
                )
            ):
                save_existing_file(path_hgrc)
            else:
                return
        self._create_hgrc_code()
        path_hgrc.write_text(self._hgrc_text)

        if not exists:
            if await self.push_screen_wait(
                QuestionScreen(
                    "A user config file has been created. Do you want to quit?"
                )
            ):
                self.app.exit()
            else:
                return

    @work
    @on(Button.Pressed, "#button_save")
    async def on_save_button_pressed(self, event: Button.Pressed) -> None:
        self.action_save_hgrc()

    @on(Input.Changed)
    def on_input_changed(self, event: Input.Changed) -> None:
        self.on_user_inputs_changed()

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self.on_user_inputs_changed()

    def on_user_inputs_changed(self):
        self.log_hgrc.clear()
        self.log_hgrc.write(self._create_hgrc_code().strip())


def init_tui(name, email, editor):
    """main TUI function for command init"""
    app = InitHgrcApp(name, email, editor)
    app.run()


def save_existing_file(path):
    now = datetime.now()
    path_saved = path.with_name(path.name + f"_{now:%Y-%m-%d_%H-%M-%S}")
    os.rename(path, path_saved)


def init_auto(name, email, editor, force, path_hgrc):
    """init without user interaction"""

    if path_hgrc.exists():
        if force:
            save_existing_file(path_hgrc)
        else:
            click.echo(f"{path_hgrc} already exists. Nothing to do.")
            return

    if editor is None:
        editor = editor_default

    text = HgrcCodeMaker().make_text(name, email, editor)
    path_hgrc.write_text(text)

    click.echo(f"configuration written in {path_hgrc}.")

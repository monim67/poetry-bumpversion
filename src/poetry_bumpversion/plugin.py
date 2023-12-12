"""Plugins provided by the package."""

from pathlib import Path
from typing import Iterator, cast

from cleo.events.console_events import TERMINATE
from cleo.events.console_terminate_event import ConsoleTerminateEvent
from cleo.events.event import Event
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.console.commands.version import VersionCommand
from poetry.core.pyproject.toml import PyProjectTOML
from poetry.plugins.application_plugin import ApplicationPlugin

try:
    from pydantic.v1 import ValidationError
except ModuleNotFoundError:  # pragma: no cover
    from pydantic import ValidationError  # type: ignore

from .models import (
    CURRENT_VERSION_MARKER,
    NEW_VERSION_MARKER,
    Instruction,
    PyProjectData,
)


class PluginException(Exception):
    """Raised by poetry-bumpversion plugin."""


class FileSkippedException(Exception):
    """Raised on exceptions while processing a file."""


class BumpVersionPlugin(ApplicationPlugin):
    """Bump version application plugin."""

    def activate(self, application: Application) -> None:
        """Activate the plugin.

        Args:
            application (Application): The poetry application hook/argument.
        """
        if application.event_dispatcher:
            application.event_dispatcher.add_listener(TERMINATE, self.on_terminate)

    def on_terminate(
        self, event: Event, event_name: str, dispatcher: EventDispatcher
    ) -> None:
        """Plugin on terminate hook/function.

        Args:
            event: Console event hook.
            event_name (str): Event name.
            dispatcher (EventDispatcher): Event dispatcher.
        """
        assert isinstance(event, ConsoleTerminateEvent)
        try:
            command = event.command
            if command.name == "version" and command.argument("version"):
                handle_version_update(cast(VersionCommand, command))
        except (PluginException, ValidationError) as exc:
            command.line(_(str(exc)), "warning")
        except Exception:  # pragma: no cover
            command.line(_("exit with error!"), "error")


def handle_version_update(command: VersionCommand) -> None:
    """Update version in files processing pyproject.toml instructions.

    Args:
        command: Executed poetry VersionCommand.

    Raises:
        PluginException: when plugin has nothing to do.
        pydantic.ValidationError: when plugin config is invalid.
    """
    pyproject = command.poetry.pyproject
    current_version = command.poetry.package.pretty_version
    version_arg = command.argument("version")
    new_version = command.increment_version(current_version, version_arg).text
    if new_version == current_version:
        raise PluginException("no change in version detected")

    instruction_count = 0
    for instruction in read_instructions(pyproject):
        instruction_count += 1
        try:
            update_version_in_file(command, instruction, current_version, new_version)
            command.info(_(f"processed file {instruction.file}"))
        except FileSkippedException as exc:
            command.line(_(f"skipped file {instruction.file}: {str(exc)}"), "warning")

    if instruction_count == 0:
        raise PluginException("nothing to do, please add file replacements")


def read_instructions(pyproject: PyProjectTOML) -> Iterator[Instruction]:
    """Parse pyproject to yield instructions.

    Args:
        pyproject: command.poetry.pyproject

    Yields:
        Instruction to process a file

    Raises:
        pydantic.ValidationError: when plugin config is invalid
    """
    plugin_config = PyProjectData(**pyproject.data).tool.poetry_bumpversion
    for replacement_config in plugin_config.replacements:
        for file_path in replacement_config.files:
            yield Instruction(
                file=Path(file_path),
                search_pattern=replacement_config.search,
                replace_pattern=replacement_config.replace,
            )
    for file_path, file_config in plugin_config.file.items():
        yield Instruction(
            file=Path(file_path),
            search_pattern=file_config.search,
            replace_pattern=file_config.replace,
        )


def update_version_in_file(
    command: VersionCommand,
    instruction: Instruction,
    current_version: str,
    new_version: str,
) -> None:
    """Process instruction to update the version in file.

    Args:
        command: Executed poetry VersionCommand.
        instruction: Instruction to process a file.
        current_version (str): The current version in file to be changed.
        new_version (str): The new version to change the current version with.

    Raises:
        FileSkippedException: when file doesn't exist or doesn't contain the search phase
    """
    if not instruction.file.exists():
        raise FileSkippedException("file not found")

    content = instruction.file.read_text()
    search_phrase = instruction.search_pattern.replace(
        CURRENT_VERSION_MARKER, current_version
    )
    replace_phrase = instruction.replace_pattern.replace(
        NEW_VERSION_MARKER, new_version
    )
    if search_phrase not in content:
        raise FileSkippedException(
            f"file doesn't contain search phrase: {search_phrase}"
        )

    if command.option("dry-run") is False:
        instruction.file.write_text(content.replace(search_phrase, replace_phrase))


def _(text: str) -> str:
    """Return formatted text for writing into console.

    Args:
        text: Text to format.
    """
    return f"poetry_bumpversion: {text}"

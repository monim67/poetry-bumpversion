from pathlib import Path

from cleo.commands.command import Command
from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import TERMINATE
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin


class BumpVersionPlugin(ApplicationPlugin):
    """Bump version plugin class"""

    def activate(self, application: Application) -> None:
        """The activate method of the plugin.

        Args:
            application (Application): The poetry application hook/argument.
        """
        application.event_dispatcher.add_listener(TERMINATE, self.on_terminate)

    def on_terminate(
        self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher
    ) -> None:
        """Plugin on terminate hook/function.

        Args:
            event (ConsoleCommandEvent): Console event hook.
            event_name (str): Event name.
            dispatcher (EventDispatcher): Event dispatcher.
        """
        command = event.command
        if command.name == "version" and command.argument("version"):
            handle_version_update(command)


def handle_version_update(command: Command) -> None:
    """Handling version updates using both file and replacement
       version updating

    Args:
        command (Command): Executed command.
    """
    content = command.poetry.file.read()
    current_version = command.poetry.package.pretty_version
    new_version = content["tool"]["poetry"]["version"]
    config = content["tool"].get("poetry_bumpversion", {})
    for replacement in config.get("replacements", []):
        for file_path in replacement.get("files", []):
            update_version_in_file(
                command, file_path, replacement, current_version, new_version
            )
    for file_path, instruction in config.get("file", {}).items():
        update_version_in_file(
            command, file_path, instruction, current_version, new_version
        )


def update_version_in_file(
    command: Command,
    file_path: str,
    instruction: dict,
    current_version: str,
    new_version: str,
) -> None:
    """Function for updating the version in file.

    Args:
        command (Command): Executed command.
        file_path (str): Path to file containing the version to be updated.
        instruction (dict): Instruction to search for desired version in file
        and replace it.
        current_version (str): The current version in file to be changed.
        new_version (str): The new version to change the current version with.
    """
    file = Path(file_path)
    if not file.exists():
        command.line(f"file {file} not found!")
        return

    content = file.read_text()
    new_content = content.replace(
        instruction.get("search", "{current_version}").replace(
            "{current_version}", current_version
        ),
        instruction.get("replace", "{new_version}").replace(
            "{new_version}", new_version
        ),
    )
    if new_content == content:
        command.line(f"file {file}: nothing to update!")
    else:
        file.write_text(new_content)

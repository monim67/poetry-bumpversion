from pathlib import Path

from cleo.events.console_command_event import ConsoleCommandEvent
from cleo.events.console_events import TERMINATE
from cleo.events.event_dispatcher import EventDispatcher
from poetry.console.application import Application
from poetry.plugins.application_plugin import ApplicationPlugin


class BumpVersionPlugin(ApplicationPlugin):
    def activate(self, application: Application):
        application.event_dispatcher.add_listener(TERMINATE, self.on_terminate)

    def on_terminate(
        self, event: ConsoleCommandEvent, event_name: str, dispatcher: EventDispatcher
    ) -> None:
        command = event.command
        if command.name == "version" and command.argument("version"):
            content = command.poetry.file.read()
            current_version = command.poetry.package.pretty_version
            new_version = content["tool"]["poetry"]["version"]
            for file_path, job in (
                content["tool"].get("poetry_bumpversion", {}).get("file", {}).items()
            ):
                file = Path(file_path)
                if not file.exists():
                    command.line(f"file {file} not found!")
                    continue
                with file.open("r+") as fp:
                    content = fp.read()
                    new_content = content.replace(
                        job.get("search", "{current_version}").replace(
                            "{current_version}", current_version
                        ),
                        job.get("replace", "{new_version}").replace(
                            "{new_version}", new_version
                        ),
                    )
                    if new_content == content:
                        command.line(f"file {file}: nothing to update!")
                    else:
                        fp.seek(0)
                        fp.write(new_content)
                        fp.truncate()

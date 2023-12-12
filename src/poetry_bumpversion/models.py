"""Pydantic models for the Plugin."""

from pathlib import Path
from typing import Dict, List

try:
    from pydantic.v1 import BaseModel
except ModuleNotFoundError:  # pragma: no cover
    from pydantic import BaseModel  # type: ignore

CURRENT_VERSION_MARKER = "{current_version}"
NEW_VERSION_MARKER = "{new_version}"


class Instruction(BaseModel):
    """Instruction to process a file for version update."""

    file: Path
    search_pattern: str = CURRENT_VERSION_MARKER
    replace_pattern: str = NEW_VERSION_MARKER


class FileConfig(BaseModel):
    """Pydantic model for File config."""

    search: str = CURRENT_VERSION_MARKER
    replace: str = NEW_VERSION_MARKER


class ReplacementConfig(FileConfig):
    """Pydantic model for Replacement config."""

    files: List[str] = []


class PluginConfig(BaseModel):
    """Pydantic model for plugin configuration extracted from pyproject.toml file."""

    file: Dict[str, FileConfig] = {}
    replacements: List[ReplacementConfig] = []


class ToolConfig(BaseModel):
    """Pydantic model for pyproject.toml [tool] section."""

    poetry_bumpversion: PluginConfig = PluginConfig()


class PyProjectData(BaseModel):
    """Pydantic model for pyproject.toml contents."""

    tool: ToolConfig

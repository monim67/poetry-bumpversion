""" Test idea taken from https://github.com/tiangolo/poetry-version-plugin """

import shutil
import subprocess
from pathlib import Path

testing_assets = Path(__file__).parent / "assets"


def copy_project(project_name: str, destination_dir: Path) -> Path:
    package_path = testing_assets / project_name
    return shutil.copytree(package_path, destination_dir / "project")


def execute_update_version_command(project_dir: Path, new_version: str):
    result = subprocess.run(
        ["poetry", "version", new_version],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    return result


def test_project_with_instructions(tmp_path: Path):
    new_version = "1.0.0"
    project_dir = copy_project("project_with_instructions", tmp_path)
    result = execute_update_version_command(project_dir, new_version)
    assert new_version in result.stdout
    for file in (
        project_dir / "test_package/__init__.py",
        project_dir / "test_package/version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()


def test_project_with_replacements(tmp_path: Path):
    new_version = "1.0.0"
    project_dir = copy_project("project_with_replacements", tmp_path)
    result = execute_update_version_command(project_dir, new_version)
    assert new_version in result.stdout
    for file in (
        project_dir / "test_package/__init__.py",
        project_dir / "test_package/version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()

""" Test idea taken from https://github.com/tiangolo/poetry-version-plugin """

import shutil
import subprocess
from pathlib import Path

testing_assets = Path(__file__).parent / "assets"


def copy_project(project_name: str, destination_dir: Path):
    package_path = testing_assets / project_name
    shutil.copytree(package_path, destination_dir, dirs_exist_ok=True)


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
    copy_project("project_with_instructions", tmp_path)
    result = execute_update_version_command(tmp_path, new_version)
    assert new_version in result.stdout
    for file in (
        tmp_path / "test_package/__init__.py",
        tmp_path / "test_package/version.py",
        tmp_path / "README.md",
    ):
        assert new_version in file.read_text()


def test_project_with_replacements(tmp_path: Path):
    new_version = "1.0.0"
    copy_project("project_with_replacements", tmp_path)
    result = execute_update_version_command(tmp_path, new_version)
    assert new_version in result.stdout
    for file in (
        tmp_path / "test_package/__init__.py",
        tmp_path / "test_package/version.py",
        tmp_path / "README.md",
    ):
        assert new_version in file.read_text()

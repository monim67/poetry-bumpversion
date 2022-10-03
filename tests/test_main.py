"""Integration tests, idea taken from https://github.com/tiangolo/poetry-version-plugin repository."""

import os
import shutil
import subprocess
from pathlib import Path

testing_assets: Path = Path(__file__).parent / "assets"
plugin_pyproject_file: Path = Path.cwd() / "pyproject.toml"


def copy_project(project_name: str, destination_dir: Path) -> Path:
    """Copy project directory tree to run tests.

    Args:
        project_name (str): Project name to be used as part of package_path.
        destination_dir (Path): The destination directory of the test.

    Returns:
        Path of the copied project directory.
    """
    package_path: Path = testing_assets / project_name
    return Path(shutil.copytree(package_path, destination_dir / "project"))


def execute_update_version_command(
    project_dir: Path, new_version: str
) -> "subprocess.CompletedProcess[str]":
    """Execute poetry version update command with coverage to track code coverage.

    Args:
        project_dir (Path): Destination of the test directory.
        new_version (str): The new version to update the test package version to.

    Returns:
        subprocess.CompletedProcess: The subprocess outcome object.
    """
    result = subprocess.run(
        [
            "coverage",
            "run",
            f"--rcfile={plugin_pyproject_file}",
            "-m",
            "poetry",
            "version",
            new_version,
        ],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if os.getenv("COVERAGE_RUN") == "true":
        coverage_path: Path = next(project_dir.glob(".coverage*"))
        shutil.move(str(coverage_path), Path.cwd())
    return result


def test_warning_when_no_change_in_version(tmp_path: Path) -> None:
    """Should display warning message when there's no change in version."""
    current_version: str = "0.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    result = execute_update_version_command(project_dir, current_version)
    assert "no change in version detected" in result.stdout


def test_warning_when_no_instruction_found(tmp_path: Path) -> None:
    """Should display warning message when no instruction found from pyproject.toml file."""
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    result = execute_update_version_command(project_dir, new_version)
    assert "nothing to do" in result.stdout


def test_warning_when_file_to_process_does_not_exist(tmp_path: Path) -> None:
    """Should display warning message when file given in an instruction is not found.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/file-to-process-does-not-exist.toml",
        project_dir / "pyproject.toml",
    )
    result = execute_update_version_command(project_dir, new_version)
    assert "not found" in result.stdout


def test_warning_when_file_doesnt_contain_search_phrase(tmp_path: Path) -> None:
    """Should display warning message when file does not contain search phrase.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/nothing-to-update-in-file.toml",
        project_dir / "pyproject.toml",
    )
    result = execute_update_version_command(project_dir, new_version)
    assert "file doesn't contain search phrase" in result.stdout


def test_project_with_instructions(tmp_path: Path) -> None:
    """Function for testing project with file instructions.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/valid-instructions.toml",
        project_dir / "pyproject.toml",
    )
    result = execute_update_version_command(project_dir, new_version)
    assert new_version in result.stdout
    for file in (
        project_dir / "sample_package/__init__.py",
        project_dir / "sample_package/_version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()


def test_project_with_replacements(tmp_path: Path) -> None:
    """Test function for using the replacement feature of the plugin.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/valid-replacements.toml",
        project_dir / "pyproject.toml",
    )
    result = execute_update_version_command(project_dir, new_version)
    assert new_version in result.stdout
    for file in (
        project_dir / "sample_package/__init__.py",
        project_dir / "sample_package/_version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()

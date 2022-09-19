""" Test idea taken from https://github.com/tiangolo/poetry-version-plugin """

import shutil
import subprocess
from pathlib import Path
from typing import List

testing_assets: Path = Path(__file__).parent / "assets"
plugin_source_dir: Path = Path(__file__).parent.parent / "poetry_bumpversion"


def copy_project(project_name: str, destination_dir: Path) -> Path:
    """Function for copying the project structure for poetry tests.

    Args:
        project_name (str): Project name to be used as part of package_path.
        destination_dir (Path): The destination directory of the test.

    Returns:
        Path: Path of the copied test directory.
    """
    package_path: Path = testing_assets / project_name
    return shutil.copytree(package_path, destination_dir / "project")


def execute_update_version_command(project_dir: Path, new_version: str) -> subprocess.CompletedProcess:
    """Executing poetry version update and running coverage to keep track of source
       code coverage.

    Args:
        project_dir (Path): Destination of the test directory.
        new_version (str): The new version to update the test package version to.

    Returns:
        subprocess.CompletedProcess: The subprocess outcome object.
    """
    result: subprocess.CompletedProcess = subprocess.run(
        [
            "coverage",
            "run",
            "--source",
            str(plugin_source_dir),
            "--parallel-mode",
            "-m",
            "poetry",
            "version",
            str(new_version),
        ],
        cwd=project_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    coverage_path: List = list(project_dir.glob(".coverage*"))[0]
    dst_coverage_path: Path = Path(__file__).parent.parent / coverage_path.name
    dst_coverage_path.write_bytes(coverage_path.read_bytes())

    return result


def test_project_with_file_not_found(tmp_path: Path) -> None:
    """Function for testing project with file instructions but
       file not found.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("project_file_not_found", tmp_path)
    result: subprocess.CompletedProcess = execute_update_version_command(project_dir, new_version)
    assert "not found" in result.stdout


def test_project_with_nothing_to_update(tmp_path: Path) -> None:
    """Function for testing project with file instructions but
       nothing to update.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "0.1.0"
    project_dir: Path = copy_project("project_with_nothing_to_update", tmp_path)
    result: subprocess.CompletedProcess = execute_update_version_command(project_dir, new_version)
    assert "nothing to update" in result.stdout


def test_project_with_instructions(tmp_path: Path) -> None:
    """Function for testing project with file instructions.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("project_with_instructions", tmp_path)
    result: subprocess.CompletedProcess = execute_update_version_command(project_dir, new_version)
    assert new_version in result.stdout
    for file in (
        project_dir / "test_package/__init__.py",
        project_dir / "test_package/version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()


def test_project_with_replacements(tmp_path: Path) -> None:
    """Test function for using the replacement feature of the plugin.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("project_with_replacements", tmp_path)
    result: subprocess.CompletedProcess = execute_update_version_command(project_dir, new_version)
    assert new_version in result.stdout
    for file in (
        project_dir / "test_package/__init__.py",
        project_dir / "test_package/version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()

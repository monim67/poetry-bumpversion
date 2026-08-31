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
    project_dir: Path,
    new_version: str,
    cwd: Path | None = None,
    extra_args: list[str] | None = None,
) -> "subprocess.CompletedProcess[str]":
    """Execute poetry version update command with coverage to track code coverage.

    Args:
        project_dir (Path): Destination of the test directory.
        new_version (str): The new version to update the test package version to.
        cwd (Path | None): Working directory for the command. Defaults to project_dir.
            When provided, uses the poetry --directory flag to point at project_dir.
        extra_args (list[str] | None): Additional CLI arguments appended after the
            version argument (e.g. ["--next-phase"]).

    Returns:
        subprocess.CompletedProcess: The subprocess outcome object.
    """
    run_from = cwd if cwd is not None else project_dir
    base_cmd = [
        "coverage",
        "run",
        f"--rcfile={plugin_pyproject_file}",
        "-m",
        "poetry",
    ]
    if cwd is not None:
        base_cmd += ["--directory", str(project_dir)]
    base_cmd += ["version", new_version]
    if extra_args:
        base_cmd += extra_args
    result = subprocess.run(
        base_cmd,
        cwd=run_from,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
    )
    if os.getenv("COVERAGE_RUN") == "true":
        coverage_path: Path = next(run_from.glob(".coverage*"))
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


def test_project_with_instructions_using_directory_flag(tmp_path: Path) -> None:
    """Test that file paths resolve relative to project_dir when using --directory flag.

    Reproduces issue #11 where relative file paths were resolved against the
    current working directory instead of the project directory when poetry was
    invoked with the -C / --directory flag.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/valid-instructions.toml",
        project_dir / "pyproject.toml",
    )
    # Run from a different working directory (not the project dir) using --directory
    other_cwd: Path = tmp_path
    result = execute_update_version_command(project_dir, new_version, cwd=other_cwd)
    assert new_version in result.stdout
    for file in (
        project_dir / "sample_package/__init__.py",
        project_dir / "sample_package/_version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()


def test_project_with_replacements_using_directory_flag(tmp_path: Path) -> None:
    """Test replacements feature resolves paths correctly with --directory flag.

    Reproduces issue #11 where relative file paths in the replacements section
    were resolved against CWD instead of the project directory.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    new_version: str = "1.0.0"
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/valid-replacements.toml",
        project_dir / "pyproject.toml",
    )
    # Run from a different working directory (not the project dir) using --directory
    other_cwd: Path = tmp_path
    result = execute_update_version_command(project_dir, new_version, cwd=other_cwd)
    assert new_version in result.stdout
    for file in (
        project_dir / "sample_package/__init__.py",
        project_dir / "sample_package/_version.py",
        project_dir / "README.md",
    ):
        assert new_version in file.read_text()


def test_next_phase_flag_is_forwarded(tmp_path: Path) -> None:
    """Tracked files must receive the --next-phase result, not a plain prerelease bump.

    Reproduces issue #18 where poetry version prerelease --next-phase advanced
    pyproject.toml to the next phase (e.g. 3.0.0b0) but the plugin rewrote
    tracked files with the plain prerelease result (3.0.0a1) because the
    --next-phase option was not forwarded to increment_version.

    Args:
        tmp_path (Path): tmp_path fixture provided by pytest.
    """
    project_dir: Path = copy_project("sample-project", tmp_path)
    shutil.copyfile(
        testing_assets / "pyproject-files/valid-instructions.toml",
        project_dir / "pyproject.toml",
    )
    # Establish a prerelease starting state
    execute_update_version_command(project_dir, "3.0.0a0")
    # Advance to the next prerelease phase
    result = execute_update_version_command(
        project_dir, "prerelease", extra_args=["--next-phase"]
    )
    expected_version: str = "3.0.0b0"
    assert expected_version in result.stdout
    for file in (
        project_dir / "sample_package/__init__.py",
        project_dir / "sample_package/_version.py",
    ):
        assert expected_version in file.read_text()

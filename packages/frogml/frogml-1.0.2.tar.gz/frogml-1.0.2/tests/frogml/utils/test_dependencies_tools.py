import os
from pathlib import Path

import pytest
from frogml_core.exceptions import FrogmlException

from frogml.utils.dependencies_tools import _dependency_files_handler


def test_valid_poetry_dependencies(tmp_path: Path):
    # Given
    lock_file = os.path.join(tmp_path, "poetry.lock")
    toml_file = os.path.join(tmp_path, "pyproject.toml")
    with open(lock_file, "w"):
        pass

    with open(toml_file, "w"):
        pass

    dependencies = [lock_file, toml_file]

    # When
    actual_result = _dependency_files_handler(dependencies, target_dir=tmp_path)

    # Given
    assert actual_result == dependencies


def test_valid_conda_dependencies(tmp_path: Path):
    # Given
    conda_file = os.path.join(tmp_path, "conda.yml")
    with open(conda_file, "w"):
        pass

    dependencies = [conda_file]

    # When
    actual_result = _dependency_files_handler(
        dependencies=dependencies, target_dir=tmp_path
    )

    # Given
    assert actual_result == dependencies


def test_valid_requirements_dependencies(tmp_path: Path):
    # Given
    conda_file = os.path.join(tmp_path, "requirements.txt")
    with open(conda_file, "w"):
        pass

    dependencies = [conda_file]

    # When
    actual_result = _dependency_files_handler(
        dependencies=dependencies, target_dir=tmp_path
    )

    # Given
    assert actual_result == dependencies


def test_valid_explicit_versions(tmp_path: Path):
    # Given
    dependencies = ["numpy==1.19.2", "pandas==1.1.3"]

    # When
    actual_result = _dependency_files_handler(
        dependencies=dependencies, target_dir=tmp_path
    )

    # Given
    assert len(actual_result) == 1
    with open(actual_result[0], "r") as file:
        file_lines = [line.strip() for line in file.readlines()]
    assert file_lines == dependencies


def test_invalid_explicit_versions(tmp_path: Path):
    # Given
    dependencies = ["numpy==1.19.2", "pandas=1.1.3"]

    # When + Then
    with pytest.raises(FrogmlException):
        _dependency_files_handler(dependencies=dependencies, target_dir=tmp_path)


def test_invalid_requirements_dependencies(tmp_path: Path):
    # Given
    conda_file = os.path.join(tmp_path, "requirements.txt")
    with open(conda_file, "w"):
        pass

    dependencies = [conda_file, "not_valid_file"]

    # When + Given
    with pytest.raises(FrogmlException):
        _dependency_files_handler(dependencies=dependencies, target_dir=tmp_path)


def test_invalid_conda_dependencies(tmp_path: Path):
    # Given
    conda_file = os.path.join(tmp_path, "cond.yml")
    with open(conda_file, "w"):
        pass

    dependencies = [conda_file]

    # When + Given
    with pytest.raises(FrogmlException):
        _dependency_files_handler(dependencies, tmp_path)


def test_not_valid_poetry_dependencies(tmp_path: Path):
    # Given
    lock_file = os.path.join(tmp_path, "poetry.lock")
    toml_file = os.path.join(tmp_path, "wrong_name.toml")
    with open(lock_file, "w"):
        pass

    with open(toml_file, "w"):
        pass

    dependencies = [lock_file, toml_file]

    # When + Then
    with pytest.raises(FrogmlException):
        _dependency_files_handler(dependencies, tmp_path)

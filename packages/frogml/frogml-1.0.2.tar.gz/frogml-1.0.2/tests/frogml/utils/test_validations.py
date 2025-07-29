import tempfile
from pathlib import Path

import pytest
from frogml_core.exceptions import FrogmlException

from frogml.utils.validations import (
    _validate_dependencies,
    _validate_properties,
    _validate_string,
    _validate_existing_path,
    _validate_model_name,
)

target_dir = tempfile.mkdtemp()


def test_validate_path_is_not_existing():
    with pytest.raises(FrogmlException):
        _validate_existing_path("tests/no/path")


def test_successful_validate_path_is_existing(tmp_path: Path):
    _validate_existing_path(tmp_path)


def test_validate_string_is_empty():
    with pytest.raises(FrogmlException):
        _validate_string("")


def test_successful_validate_string_is_not_empty():
    _validate_string("test")


def test_validate_properties_is_not_dict():
    with pytest.raises(ValueError):
        _validate_properties("test")


def test_validate_properties_keys_values_string():
    _validate_properties({"key": "value"})


def test_validate_properties_keys_values_not_string():
    with pytest.raises(FrogmlException):
        _validate_properties({"key": 1})


def test_validate_dependencies_is_not_list():
    with pytest.raises(ValueError):
        _validate_dependencies("test")


def test_validate_dependencies_is_list_of_strings():
    _validate_dependencies(["test"])


def test_name_is_empty():
    with pytest.raises(FrogmlException):
        _validate_model_name("")


def test_name_is_too_long():
    with pytest.raises(FrogmlException):
        _validate_model_name("a" * 61)


def test_name_is_invalid():
    with pytest.raises(FrogmlException):
        _validate_model_name("name with spaces")
    with pytest.raises(FrogmlException):
        _validate_model_name("name.with.dots.")
    with pytest.raises(FrogmlException):
        _validate_model_name("name_with_underscores.")

import os
import platform
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List

import pytest
from frogml_core.exceptions import FrogmlException

from frogml.utils.files_tools import _zip_dir


def test_zip_model_success(tmp_path: Path):
    # Given
    files_list = ["file1.py", "file2.py", ".hidden_file.py", ".dvc"]
    dir_path = given_a_directory_with_files(files_list)

    # When
    zip_file = _zip_dir(root_dir=tmp_path, dir_to_zip=dir_path)

    with tempfile.TemporaryDirectory() as temp_extract_dir:
        shutil.unpack_archive(zip_file, temp_extract_dir)
        extracted_files: List[str] = os.listdir(temp_extract_dir)

    # Then
    expected_files = ["file1.py", "file2.py", ".dvc"]
    for actual_files in expected_files:
        assert actual_files in extracted_files


@pytest.mark.skipif(
    "3.10" <= platform.python_version() < "3.11",
    reason="Problematic test for Python 3.10",
)
def test_zip_model_error_on_zipping(tmp_path: Path):
    # Given
    dir_path: str = uuid.uuid4()

    # When + Then
    with pytest.raises(FrogmlException) as exception_info:
        _zip_dir(root_dir=tmp_path, dir_to_zip=dir_path)

    assert "Unable to zip model" in str(exception_info.value)


def given_a_directory_with_files(files: List[str]) -> str:
    test_dir: str = tempfile.mkdtemp()

    for file in files:
        with open(os.path.join(test_dir, file), "w"):
            pass

    return test_dir


def given_full_path_to_file(file_name: str) -> str:
    json_file_path: str = os.path.join(os.path.dirname(__file__), file_name)

    return os.path.abspath(json_file_path)

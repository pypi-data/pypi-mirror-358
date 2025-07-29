import json
import os
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch, ANY, MagicMock

import pytest
from frogml_core.exceptions import FrogmlException
from frogml_proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from frogml_storage.frog_ml import FrogMLStorage
from frogml_storage.models.frogml_model_version import FrogMLModelVersion

from frogml.python import _PYTHON_MODEL_FLAVOR
from frogml.python import log_model, get_model_info, load_model
from tests.frogml.utils.test_files_tools import given_full_path_to_file
from tests.resources.models.python.regression_func import predict


@pytest.mark.parametrize(
    "given_frogml_model_version", [["python", platform.version(), "pkl"]], indirect=True
)
@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.upload_model_version")
@patch("shutil.rmtree")
def test_log_model(
    _,
    mock_upload_model_version,
    jf_project: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
    given_frogml_model_version: FrogMLModelVersion,
):
    # Given
    repository = "repository"
    name = "name"
    version = "version"
    properties = {"key": "value"}
    dependencies = ["pandas==1.2.3"]
    full_code_dir = os.path.join(models_resources_dir_path, "classes")
    frogml_services_mock.repository_service.repositories[repository] = RepositorySpec(
        project_key=jf_project
    )
    mock_upload_model_version.return_value = given_frogml_model_version

    # When
    log_model(
        function=predict,
        model_name=name,
        repository=repository,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=full_code_dir,
    )

    # Then
    # validate passed arguments
    mock_upload_model_version.assert_called_once_with(
        repository=repository,
        model_name=name,
        model_path=ANY,
        model_type=ANY,
        version=version,
        properties=properties,
        dependencies_files_paths=ANY,
        code_archive_file_path=ANY,
    )

    # validate model path
    model_path = Path(mock_upload_model_version.call_args.kwargs["model_path"])
    assert model_path.name == f"{name}.pkl"

    # validate model type
    model_metadata = mock_upload_model_version.call_args.kwargs["model_type"]
    assert model_metadata.framework == _PYTHON_MODEL_FLAVOR
    assert model_metadata.framework_version == platform.python_version()
    assert model_metadata.serialization_format == "pkl"
    assert model_metadata.runtime == "python"
    assert model_metadata.runtime_version == platform.python_version()

    # validate dependencies
    dependencies_files_paths = mock_upload_model_version.call_args.kwargs[
        "dependencies_files_paths"
    ][0]
    with open(dependencies_files_paths, "r") as dependencies_file:
        dependencies_list = [line.strip() for line in dependencies_file.readlines()]
        assert len(dependencies_list) == len(dependencies)
        for dependency in dependencies:
            assert dependency in dependencies_list

    # validate code archive
    archive_path = Path(
        mock_upload_model_version.call_args.kwargs["code_archive_file_path"]
    )
    assert archive_path.exists()
    assert archive_path.suffix == ".zip"


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
def test_get_model_info(get_entity_info_mock):
    # Given
    repository = "repository"
    model_name = "model_name"
    version = "version"
    json_file_path = "../../../tests/resources/models/python/python_model_info.json"
    json_full_path = given_full_path_to_file(file_name=json_file_path)

    with open(json_full_path, "r") as json_file:
        model_info = json.load(json_file)

    get_entity_info_mock.return_value = model_info

    # When
    actual_result = get_model_info(
        repository=repository, model_name=model_name, version=version
    )

    # Then
    assert actual_result == model_info


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
@patch("frogml_storage.frog_ml.FrogMLStorage.download_model_version")
def test_load_model(download_model_version_mock, get_entity_info_mock):
    # Given
    repository = "repository"
    model_name = "model_name"
    version = "version"
    json_file_path = "../../../tests/resources/models/python/python_model_info.json"
    full_json_path = given_full_path_to_file(file_name=json_file_path)

    with open(full_json_path, "r") as json_file:
        model_info = json.load(json_file)

    get_entity_info_mock.return_value = model_info
    full_model_dir_path = given_full_path_to_file(
        file_name="../../../tests/resources/models/python"
    )
    download_model_version_mock.return_value = Path(full_model_dir_path)

    # When
    with patch.object(tempfile, "TemporaryDirectory") as mock_tempdir:
        mock_tempdir_instance = MagicMock()
        mock_tempdir.return_value = mock_tempdir_instance
        mock_tempdir_instance.__enter__.return_value = full_model_dir_path
        download_model_version_mock.return_value = Path(full_model_dir_path)
        returned_func = load_model(
            repository=repository, model_name=model_name, version=version
        )

        # Then
        assert returned_func.__code__ == predict.__code__


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
@patch("frogml_storage.frog_ml.FrogMLStorage.download_model_version")
def test_load_model_wrong_model_type(download_model_version_mock, get_entity_info_mock):
    # Given
    repository = "repository"
    model_name = "model_name"
    version = "version"
    json_file_path = "../../resources/models/files/tensorflow_model_info.json"
    some_path = "some_path"
    expected_path = Path(some_path)
    json_full_path = given_full_path_to_file(file_name=json_file_path)

    with open(json_full_path, "r") as json_file:
        model_info = json.load(json_file)

    get_entity_info_mock.return_value = model_info
    download_model_version_mock.return_value = expected_path

    # When + Then
    with pytest.raises(FrogmlException):
        load_model(repository=repository, model_name=model_name, version=version)

import json
import os
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch, ANY, MagicMock

import pytest
import torch
from frogml_core.exceptions import FrogmlException
from frogml_proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from frogml_storage.frog_ml import FrogMLStorage
from frogml_storage.models.frogml_model_version import FrogMLModelVersion

from frogml.pytorch import (
    log_model,
    _PYTORCH_MODEL_FLAVOR,
    get_model_info,
    load_model,
)
from frogml.pytorch import pickle_module as pytorch_pickle_module
from tests.frogml.pytorch.test_pickle_module import assert_same_pytorch_model
from tests.frogml.utils.test_files_tools import given_full_path_to_file
from tests.resources.models.pytorch.pytorch_nn_model import (
    get_train_data,
    get_trained_model,
)


@pytest.mark.parametrize(
    "given_frogml_model_version",
    [["pytorch", torch.__version__, "torch"]],
    indirect=True,
)
@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.upload_model_version")
@patch("shutil.rmtree")
def test_log_model(
    _,
    mock_upload_model_version: MagicMock,
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

    train_data_path = os.path.join(
        models_resources_dir_path, "pytorch", "pima-indians-diabetes.data.csv"
    )
    train_data_input, train_data_output = get_train_data(train_data_path)
    model = get_trained_model(train_data_input, train_data_output)
    mock_upload_model_version.return_value = given_frogml_model_version

    # When
    log_model(
        model=model,
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

    # validate model type
    model_metadata = mock_upload_model_version.call_args.kwargs["model_type"]
    torch_version_base_only = model_metadata.framework_version.split("+")[
        0
    ]  # torch includes compute backend version such as +cu124 or +cpu
    assert model_metadata.framework == _PYTORCH_MODEL_FLAVOR
    assert torch_version_base_only == torch.__version__.split("+")[0]
    assert model_metadata.serialization_format == "pth"
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
    assert archive_path.suffix == ".zip"
    assert archive_path.exists()


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
def test_get_model_info(get_entity_info_mock):
    # Given
    repository = "repository"
    model_name = "model_name"
    version = "version"
    json_file_path = "../../../tests/resources/models/pytorch/pytorch_model_info.json"
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
    model_name = "pytorch_model"
    version = "version"
    json_file_path = "../../../tests/resources/models/pytorch/pytorch_model_info.json"
    full_json_path = given_full_path_to_file(file_name=json_file_path)

    with open(full_json_path, "r") as json_file:
        model_info = json.load(json_file)

    get_entity_info_mock.return_value = model_info
    full_model_dir_path = given_full_path_to_file(
        file_name="../../../tests/resources/models/pytorch"
    )

    train_data_path = (
        "../../../tests/resources/models/pytorch/pima-indians-diabetes.data.csv"
    )
    full_train_data_path = given_full_path_to_file(file_name=train_data_path)
    train_data_input, train_data_output = get_train_data(full_train_data_path)
    trained_model = get_trained_model(train_data_input, train_data_output)

    with patch.object(tempfile, "TemporaryDirectory") as mock_tempdir:
        mock_tempdir_instance = MagicMock()
        mock_tempdir.return_value = mock_tempdir_instance
        mock_tempdir_instance.__enter__.return_value = full_model_dir_path
        download_model_version_mock.return_value = Path(full_model_dir_path)

        torch.save(
            obj=trained_model,
            f=f"{full_model_dir_path}/{model_name}.pth",
            pickle_module=pytorch_pickle_module,
        )

        download_model_version_mock.return_value = Path(full_model_dir_path)

        # When
        deserialized_model = load_model(
            repository=repository, model_name=model_name, version=version
        )

        # Then
        assert_same_pytorch_model(trained_model, deserialized_model, train_data_input)


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
@patch("frogml_storage.frog_ml.FrogMLStorage.download_model_version")
def test_load_model_failed_deserialized(
    download_model_version_mock, get_entity_info_mock
):
    # Given
    repository = "repository"
    model_name = "pytorch_model"
    version = "version"
    json_file_path = "../../../tests/resources/models/pytorch/pytorch_model_info.json"
    full_json_path = given_full_path_to_file(file_name=json_file_path)

    with open(full_json_path, "r") as json_file:
        model_info = json.load(json_file)

    get_entity_info_mock.return_value = model_info
    full_model_dir_path = given_full_path_to_file(
        file_name="../../../tests/resources/models/files"
    )
    download_model_version_mock.return_value = Path(full_model_dir_path)

    # When + Then
    with pytest.raises(Exception):
        load_model(repository=repository, model_name=model_name, version=version)


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

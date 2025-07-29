import json
import os.path
import platform
import tempfile
from pathlib import Path
from unittest.mock import patch, ANY, MagicMock

import pytest
from frogml_proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from frogml_storage.frog_ml import FrogMLStorage
from frogml_storage.models.frogml_model_version import FrogMLModelVersion
from transformers import (
    DistilBertModel,
    DistilBertTokenizer,
    __version__ as transformers_version,
)

from frogml.huggingface import (
    log_model,
    _HUGGINGFACE_LEARN_MODEL_FLAVOR,
    get_model_info,
    load_model,
)
from tests.frogml.utils.test_files_tools import given_full_path_to_file


@pytest.mark.parametrize(
    "given_frogml_model_version", [["huggingface", "1.0.0", "hf"]], indirect=True
)
@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.upload_model_version")
def test_log_model(
    mock_upload_model_version: MagicMock,
    given_huggingface_model_path: Path,
    jf_project: str,
    frogml_services_mock: FrogmlMocks,
    given_frogml_model_version: FrogMLModelVersion,
):
    # Given
    repository = "repository"
    model_name = "name"
    version = "version"
    properties = {"key": "value"}
    dependencies = ["pandas==1.2.3"]

    full_model_dir = given_full_path_to_file(
        file_name=os.path.join(given_huggingface_model_path, "distilbert_model")
    )
    model = DistilBertModel.from_pretrained(full_model_dir)
    tokenizer = DistilBertTokenizer.from_pretrained(full_model_dir)
    frogml_services_mock.repository_service.repositories[repository] = RepositorySpec(
        project_key=jf_project
    )

    with patch.object(tempfile, "TemporaryDirectory") as mock_tempdir:
        mock_tempdir_instance = MagicMock()
        mock_tempdir.return_value = mock_tempdir_instance
        mock_tempdir_instance.__enter__.return_value = given_huggingface_model_path
        mock_upload_model_version.return_value = given_frogml_model_version

        # When
        log_model(
            model=model,
            tokenizer=tokenizer,
            model_name=model_name,
            repository=repository,
            version=version,
            properties=properties,
            dependencies=dependencies,
        )

        # Then
        # validate passed arguments
        mock_upload_model_version.assert_called_once_with(
            repository=repository,
            model_name=model_name,
            model_path=ANY,
            model_type=ANY,
            version=version,
            properties=properties,
            dependencies_files_paths=ANY,
            code_archive_file_path=ANY,
        )

        # validate model type
        model_metadata = mock_upload_model_version.call_args.kwargs["model_type"]
        assert model_metadata.framework == _HUGGINGFACE_LEARN_MODEL_FLAVOR
        assert model_metadata.framework_version == transformers_version
        assert model_metadata.serialization_format == "pretrained_model"
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


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
def test_get_model_info(get_entity_info_mock):
    # Given
    repository = "repository"
    model_name = "model_name"
    version = "version"
    json_file_path = (
        "../../../tests/resources/models/huggingface/huggingface_model_info.json"
    )
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
def test_load_model(
    download_model_version_mock,
    get_entity_info_mock,
    given_huggingface_model_path: Path,
):
    # Given
    repository = "repository"
    model_name = "distilbert_model"
    version = "version"
    json_file_path = (
        "../../../tests/resources/models/huggingface/huggingface_model_info.json"
    )
    full_json_path = given_full_path_to_file(file_name=json_file_path)
    with patch.object(tempfile, "TemporaryDirectory") as mock_tempdir:
        mock_tempdir_instance = MagicMock()
        mock_tempdir.return_value = mock_tempdir_instance
        mock_tempdir_instance.__enter__.return_value = given_huggingface_model_path

        with open(full_json_path, "r") as json_file:
            model_info = json.load(json_file)

        get_entity_info_mock.return_value = model_info
        full_model_dir_path = given_full_path_to_file(
            file_name=given_huggingface_model_path
        )
        download_model_version_mock.return_value = Path(full_model_dir_path)

        # When
        deserialized_model, deserialized_tokenizer = load_model(
            repository=repository, model_name=model_name, version=version
        )

        # Then
        isinstance(deserialized_model, DistilBertModel)
        isinstance(deserialized_tokenizer, DistilBertTokenizer)


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
@patch("frogml_storage.frog_ml.FrogMLStorage.download_model_version")
def test_load_model_failed_deserialized(
    download_model_version_mock, get_entity_info_mock
):
    # Given
    repository = "repository"
    model_name = "random_forest_model"
    version = "version"
    json_file_path = (
        "../../../tests/resources/models/huggingface/huggingface_model_info.json"
    )
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

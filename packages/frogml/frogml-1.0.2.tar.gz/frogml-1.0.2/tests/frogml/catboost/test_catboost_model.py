import json
import os.path
import platform
import tempfile
import uuid
from pathlib import Path
from unittest.mock import patch, ANY, MagicMock

import pytest
from catboost import CatBoostClassifier, __version__ as catboost_version
from frogml_core.exceptions import FrogmlException
from frogml_proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from frogml_storage.frog_ml import FrogMLStorage
from frogml_storage.model_manifest import ModelManifest
from frogml_storage.models.frogml_model_version import FrogMLModelVersion
from frogml_storage.serialization_metadata import SerializationMetadata
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

from frogml.catboost import (
    log_model,
    _CATBOOST_MODEL_FLAVOR,
    get_model_info,
    load_model,
)
from tests.frogml.utils.test_files_tools import given_full_path_to_file


@pytest.mark.parametrize(
    "given_frogml_model_version", [["catboost", catboost_version, "cbm"]], indirect=True
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
    model_name = "model-name"
    version = "version"
    properties = {"key": "value"}
    dependencies = ["pandas==1.2.3"]

    # Path to the models repo
    loaded_model = CatBoostClassifier()
    loaded_model = loaded_model.load_model(
        os.path.join(models_resources_dir_path, "catboost", "catboost_model.cbm")
    )
    full_code_dir = os.path.join(models_resources_dir_path, "classes")

    frogml_services_mock.repository_service.repositories[repository] = RepositorySpec(
        project_key=jf_project
    )
    mock_upload_model_version.return_value = FrogMLModelVersion(
        entity_name=str(uuid.uuid4()),
        namespace=None,
        version=version,
        entity_manifest=ModelManifest(
            created_date="now",
            artifacts=[],
            id=None,
            model_format=SerializationMetadata(
                framework="catboost",
                framework_version=catboost_version,
                serialization_format="cbm",
                runtime="python",
                runtime_version=platform.python_version(),
            ),
            dependency_artifacts=[],
            code_artifacts=None,
        ),
    )

    # When
    log_model(
        model=loaded_model,
        model_name=model_name,
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
    assert model_metadata.framework == _CATBOOST_MODEL_FLAVOR
    assert model_metadata.framework_version == catboost_version
    assert model_metadata.serialization_format == "cbm"
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
    json_file_path = "../../../tests/resources/models/catboost/catboost_model_info.json"
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
    model_name = "catboost_model"
    version = "version"
    json_file_path = "../../../tests/resources/models/catboost/catboost_model_info.json"
    full_json_path = given_full_path_to_file(file_name=json_file_path)

    with open(full_json_path, "r") as json_file:
        model_info = json.load(json_file)

    get_entity_info_mock.return_value = model_info
    full_model_dir_path = given_full_path_to_file(
        file_name="../../../tests/resources/models/catboost"
    )

    with patch.object(tempfile, "TemporaryDirectory") as mock_tempdir:
        mock_tempdir_instance = MagicMock()
        mock_tempdir.return_value = mock_tempdir_instance
        mock_tempdir_instance.__enter__.return_value = full_model_dir_path
        download_model_version_mock.return_value = Path(full_model_dir_path)

        # When
        deserialized_model = load_model(
            repository=repository, model_name=model_name, version=version
        )

        # Then
        _predict_catboost_model(deserialized_model)


@patch.object(FrogMLStorage, "__init__", lambda _: None)
@patch("frogml_storage.frog_ml.FrogMLStorage.get_entity_manifest")
@patch("frogml_storage.frog_ml.FrogMLStorage.download_model_version")
def test_load_model_failed_deserialized(
    download_model_version_mock, get_entity_info_mock
):
    # Given
    repository = "repository"
    model_name = "catboost_model"
    version = "version"
    json_file_path = "../../../tests/resources/models/catboost/catboost_model_info.json"
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


def _predict_catboost_model(model: CatBoostClassifier):
    # Load a sample dataset (Iris dataset)
    iris = load_iris()
    X = iris.data
    y = iris.target
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    # Make predictions on the test set
    y_pred = model.predict(X_test)

    # Calculate accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy * 100: .2f}%")

    print("Feature Importances: ", model.get_feature_importance())


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

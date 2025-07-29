import os
from pathlib import Path
from typing import Dict

import catboost
import joblib
import onnx
import pytest
import sklearn
import torch
import transformers
from frogml_proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from onnx import ModelProto
from sklearn.ensemble import RandomForestClassifier
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

import frogml.catboost
from tests.frogml.utils.test_files_tools import given_full_path_to_file
from tests.resources.models.python.regression_func import predict
from tests.resources.models.pytorch.pytorch_nn_model import (
    get_train_data,
    get_trained_model,
    PimaClassifier,
)


# Add a test when the repo is not in a project


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_onnx(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "onnx_model_name"
    dependencies = [given_full_path_to_file("../../../pyproject.toml")]
    version = "onnx_version_1"
    properties = {"key": "value", "key2": "value2"}
    code_dir = os.path.join(models_resources_dir_path, "classes")
    model_type = "onnx"
    expected_runtime_version = given_runtime_version

    expected_framework_version = onnx.__version__

    loaded_catboost_model = onnx.load(
        os.path.join(given_resource_path, model_type, "simple_model.onnx")
    )
    onnx.checker.check_model(loaded_catboost_model)
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # When
    frogml.onnx.log_model(
        model=loaded_catboost_model,
        model_name=model_name,
        repository=repository_in_project,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.onnx.get_model_info(
        repository=repository_in_project, model_name=model_name, version=version
    )

    actual_model = frogml.onnx.load_model(repository_in_project, model_name, version)

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework=model_type,
        expected_runtime="python",
        expected_serialization_format=model_type,
        expected_framework_version=expected_framework_version,
        expected_runtime_version=expected_runtime_version,
        expected_dependency_file="pyproject.toml",
    )

    assert isinstance(actual_model, ModelProto)


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_catboost(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "catboost_model_name"
    dependencies = ["catboost==0.26.1"]
    version = "catboost_version_1"
    properties = {"key": "value"}
    code_dir = os.path.join(models_resources_dir_path, "classes")
    expected_serialization_format = "cbm"
    repository = repository_in_project
    model_type = "catboost"
    expected_runtime_version = given_runtime_version
    expected_framework_version = catboost.__version__

    from catboost import CatBoostClassifier

    catboost_classifier = CatBoostClassifier()
    loaded_catboost_model = catboost_classifier.load_model(
        os.path.join(given_resource_path, model_type, "catboost_model.cbm")
    )
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # when
    frogml.catboost.log_model(
        model=loaded_catboost_model,
        model_name=model_name,
        repository=repository,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.catboost.get_model_info(
        repository=repository, model_name=model_name, version=version
    )

    actual_model = frogml.catboost.load_model(repository, model_name, version)

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework=model_type,
        expected_runtime="python",
        expected_serialization_format=expected_serialization_format,
        expected_framework_version=expected_framework_version,
        expected_runtime_version=expected_runtime_version,
        expected_dependency_file="requirements.txt",
    )

    assert isinstance(actual_model, CatBoostClassifier)


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_pytorch(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "pytorch_model_name"
    dependencies = ["pandas==0.26.1"]
    version = "pytorch_version_1"
    properties = {"key": "value"}
    code_dir = os.path.join(models_resources_dir_path, "classes")
    repository = repository_in_project
    expected_runtime_version = given_runtime_version
    expected_framework_version = torch.__version__

    train_data_path = (
        "../../../tests/resources/models/pytorch/pima-indians-diabetes.data.csv"
    )
    full_train_data_path = given_full_path_to_file(file_name=train_data_path)
    train_data_input, train_data_output = get_train_data(full_train_data_path)
    model = get_trained_model(train_data_input, train_data_output)
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # when
    frogml.pytorch.log_model(
        model=model,
        model_name=model_name,
        repository=repository,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.pytorch.get_model_info(
        repository=repository, model_name=model_name, version=version
    )

    actual_model = frogml.pytorch.load_model(repository, model_name, version)

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework="pytorch",
        expected_runtime="python",
        expected_serialization_format="pth",
        expected_framework_version=expected_framework_version,
        expected_runtime_version=expected_runtime_version,
        expected_dependency_file="requirements.txt",
    )

    assert isinstance(actual_model, PimaClassifier)


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_scikit_learn(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "scikit_learn_model_name"
    dependencies = ["pandas==0.26.1"]
    version = "scikit_learn_version_1"
    properties = {"key": "value"}
    code_dir = os.path.join(models_resources_dir_path, "classes")
    repository = repository_in_project
    expected_runtime_version = given_runtime_version
    expected_framework_version = sklearn.__version__

    model_dir = "../../../tests/resources/models/scikit_learn"
    full_model_dir = given_full_path_to_file(file_name=model_dir)
    loaded_model = joblib.load(
        os.path.join(full_model_dir, "random_forest_model.joblib")
    )
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # when
    frogml.scikit_learn.log_model(
        model=loaded_model,
        model_name=model_name,
        repository=repository,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.scikit_learn.get_model_info(
        repository=repository, model_name=model_name, version=version
    )

    actual_model = frogml.scikit_learn.load_model(repository, model_name, version)

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework="scikit_learn",
        expected_runtime="python",
        expected_serialization_format="joblib",
        expected_framework_version=expected_framework_version,
        expected_runtime_version=expected_runtime_version,
        expected_dependency_file="requirements.txt",
    )

    assert isinstance(actual_model, RandomForestClassifier)


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_python_model(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "python_model_name"
    dependencies = ["catboost==0.26.1"]
    version = "python_version_1"
    properties = {"key": "value"}
    code_dir = os.path.join(models_resources_dir_path, "classes")

    expected_runtime_version = given_runtime_version
    expected_framework_version = given_runtime_version
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # when
    frogml.python.log_model(
        function=predict,
        model_name=model_name,
        repository=repository_in_project,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.python.get_model_info(
        repository=repository_in_project, model_name=model_name, version=version
    )

    actual_model = frogml.python.load_model(repository_in_project, model_name, version)

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework="python",
        expected_runtime="python",
        expected_serialization_format="pkl",
        expected_framework_version=expected_framework_version,
        expected_runtime_version=expected_runtime_version,
        expected_dependency_file="requirements.txt",
    )
    assert isinstance(actual_model(123), float)


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_huggingface(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    given_huggingface_model_path: Path,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "huggingface_model_name"
    version = "huggingface_version_1"
    properties = {"key": "value"}
    code_dir = os.path.join(models_resources_dir_path, "classes")
    dependencies = ["catboost==0.26.1"]
    repository = repository_in_project
    model_version = transformers.__version__
    full_model_dir = given_full_path_to_file(
        file_name=os.path.join(given_huggingface_model_path, "distilbert_model")
    )

    model = DistilBertForSequenceClassification.from_pretrained(full_model_dir)
    tokenizer = DistilBertTokenizer.from_pretrained(full_model_dir)
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # when
    frogml.huggingface.log_model(
        model=model,
        tokenizer=tokenizer,
        model_name=model_name,
        repository=repository,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.huggingface.get_model_info(
        repository=repository, model_name=model_name, version=version
    )

    actual_model, actual_tokenizer = frogml.huggingface.load_model(
        repository, model_name, version
    )

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework="huggingface",
        expected_runtime="python",
        expected_serialization_format="pretrained_model",
        expected_framework_version=model_version,
        expected_runtime_version=given_runtime_version,
        expected_dependency_file="requirements.txt",
    )

    assert isinstance(actual_model, DistilBertForSequenceClassification)
    assert isinstance(actual_tokenizer, DistilBertTokenizer)


@pytest.mark.integration
@pytest.mark.parametrize(
    "is_subscribed_to_jml",
    [True, False],
    ids=["subscribed_jml_customer", "not_subscribed_jml_customer"],
)
def test_e2e_files(
    is_subscribed_to_jml: bool,
    jf_project: str,
    repository_in_project: str,
    given_resource_path: str,
    given_runtime_version: str,
    frogml_services_mock: FrogmlMocks,
    models_resources_dir_path: str,
):
    # Given
    model_name = "files_model_name"
    dependencies = ["catboost==0.26.1"]
    version = "files_version_1"
    properties = {"key": "value"}
    code_dir = os.path.join(models_resources_dir_path, "classes")
    repository = repository_in_project
    expected_runtime_version = given_runtime_version

    source_path = "../../resources/models/files/pickled_model.pkl"
    full_source_path = given_full_path_to_file(file_name=source_path)
    frogml_services_mock.repository_service.repositories[repository_in_project] = (
        RepositorySpec(project_key=jf_project)
    )
    # If the customer is not subscribed to JML, we should raise an exception
    frogml_services_mock.jfrog_tenant_info_service.should_raise_exception = (
        not is_subscribed_to_jml
    )

    # when
    frogml.files.log_model(
        source_path=full_source_path,
        repository=repository,
        model_name=model_name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

    model_info = frogml.files.get_model_info(
        repository=repository, model_name=model_name, version=version
    )

    actual_model_path = frogml.files.load_model(repository, model_name, version)

    # Then
    _assert_model_info(
        model_info=model_info,
        model_name=model_name,
        version=version,
        expected_framework="files",
        expected_runtime="python",
        expected_serialization_format="pkl",
        expected_framework_version="",
        expected_runtime_version=expected_runtime_version,
        expected_dependency_file="requirements.txt",
    )

    assert os.path.exists(actual_model_path)


def _assert_model_info(
    model_info: Dict,
    model_name: str,
    version: str,
    expected_framework: str,
    expected_runtime: str,
    expected_serialization_format: str,
    expected_framework_version: str,
    expected_runtime_version: str,
    expected_dependency_file: str,
):
    model_format = model_info.get("model_format")
    code_artifacts = model_info.get("code_artifacts")[0]
    dependency_artifacts = model_info.get("dependency_artifacts")[0]

    actual_download_url = code_artifacts["download_url"]
    assert code_artifacts.get("artifact_path") == "code.zip"
    assert str(actual_download_url).__contains__(
        f"models/{model_name}/{version}/code/code.zip"
    )
    assert model_format["framework"] == expected_framework
    assert model_format["runtime"] == expected_runtime
    assert model_format["serialization_format"] == expected_serialization_format
    assert model_format["framework_version"] == expected_framework_version
    assert model_format["runtime_version"] == expected_runtime_version
    assert dependency_artifacts["artifact_path"] == expected_dependency_file

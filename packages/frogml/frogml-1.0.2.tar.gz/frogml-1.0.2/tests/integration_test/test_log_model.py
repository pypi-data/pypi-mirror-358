import os

import onnx
import pytest
from frogml_core.exceptions import FrogmlException
from frogml_core.utils.proto_utils import ONNX_FRAMEWORK_FORMAT
from frogml_proto.qwak.jfrog.gateway.v0.repository_pb2 import RepositorySpec
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks

import frogml
from tests.frogml.utils.test_files_tools import given_full_path_to_file


def __get_log_model_arguments(resource_path: str, repo_key: str) -> dict:
    model_name = "onnx_model_name"
    dependencies = [given_full_path_to_file("../../../pyproject.toml")]
    version = "onnx_version_1"
    properties = {"key": "value", "key2": "value2"}
    code_dir = given_full_path_to_file("../../../tests/frogml/onnx")

    loaded_catboost_model = onnx.load(
        os.path.join(resource_path, ONNX_FRAMEWORK_FORMAT, "simple_model.onnx")
    )
    onnx.checker.check_model(loaded_catboost_model)

    return {
        "model": loaded_catboost_model,
        "model_name": model_name,
        "repository": repo_key,
        "version": version,
        "properties": properties,
        "dependencies": dependencies,
        "code_dir": code_dir,
    }


@pytest.mark.integration
def test_e2e_when_repo_doesnt_exist_then_error(
    repository_not_in_project: str,
    given_resource_path: str,
    frogml_services_mock: FrogmlMocks,
):
    # Given
    arguments: dict = __get_log_model_arguments(
        given_resource_path, repository_not_in_project
    )

    # When
    with pytest.raises(FrogmlException) as ex:
        frogml.onnx.log_model(**arguments)

    assert isinstance(ex.value, FrogmlException)
    assert f"Repository {repository_not_in_project} not found" in ex.value.message


@pytest.mark.integration
def test_e2e_when_repo_doesnt_belong_to_any_project_then_error(
    repository_not_in_project: str,
    given_resource_path: str,
    frogml_services_mock: FrogmlMocks,
):
    # Given
    arguments: dict = __get_log_model_arguments(
        given_resource_path, repository_not_in_project
    )
    frogml_services_mock.repository_service.repositories[repository_not_in_project] = (
        RepositorySpec()
    )

    # When
    with pytest.raises(ValueError) as ex:
        frogml.onnx.log_model(**arguments)

    assert isinstance(ex.value, ValueError)
    assert (
        f"Repository '{repository_not_in_project}' does not belong to any project"
        == ex.value.args[0]
    )

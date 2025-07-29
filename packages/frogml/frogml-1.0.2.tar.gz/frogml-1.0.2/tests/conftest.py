import os
import platform
import uuid
from concurrent import futures
from pathlib import Path
from platform import python_version
from typing import Generator

import grpc
import pytest
from _pytest.fixtures import fixture, SubRequest
from frogml_services_mock.mocks.frogml_mocks import FrogmlMocks
from frogml_services_mock.services_mock import frogml_container, attach_servicers
from frogml_storage.model_manifest import ModelManifest
from frogml_storage.models.frogml_model_version import FrogMLModelVersion
from frogml_storage.serialization_metadata import SerializationMetadata
from transformers import DistilBertModel, DistilBertTokenizer

from tests.frogml.utils.test_files_tools import given_full_path_to_file


@pytest.fixture
def frogml_services_mock() -> Generator[FrogmlMocks, None, None]:
    free_port: int = frogml_container()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    qwak_mocks = attach_servicers(free_port, server)

    server.add_insecure_port(f"[::]:{free_port}")
    server.start()

    yield qwak_mocks

    server.stop(0)


@pytest.fixture
def resource_folder() -> str:
    resource_path: str = "../../../tests/resources"

    return os.path.abspath(resource_path)


@pytest.fixture(scope="session")
def jf_project() -> str:
    return "tests-project"


@fixture(scope="session")
def repository_in_project(jf_project: str) -> str:
    return f"{jf_project}-test-ml-repo2"


@fixture(scope="session")
def repository_not_in_project() -> str:
    return "test-ml-repo3"


@pytest.fixture
def given_resource_path() -> str:
    return given_full_path_to_file("../../../tests/resources/models")


@pytest.fixture
def given_runtime_version() -> str:
    return python_version()


@pytest.fixture
def given_huggingface_model_path(tmp_path: Path) -> Path:
    """
    Fixture to create a Hugging Face model, save it to a temporary directory,
    return the path to the directory.
    """
    model = DistilBertModel.from_pretrained("distilbert-base-uncased")
    tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
    model_path = os.path.join(tmp_path, "distilbert_model")

    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)

    return tmp_path


@pytest.fixture(scope="session")
def resource_dir_path() -> str:
    return os.path.abspath(Path(__file__).resolve().parent / "resources")


@pytest.fixture(scope="session")
def models_resources_dir_path(resource_dir_path: str) -> str:
    return os.path.join(resource_dir_path, "models")


@pytest.fixture
def given_frogml_model_version(request: SubRequest) -> FrogMLModelVersion:
    """
    Fixture to return a FrogML model version string.
    """
    return FrogMLModelVersion(
        entity_name=str(uuid.uuid4()),
        namespace=None,
        version=str(uuid.uuid4()),
        entity_manifest=ModelManifest(
            created_date="now",
            artifacts=[],
            id=None,
            model_format=SerializationMetadata(
                framework=request.param[0],
                framework_version=request.param[1],
                serialization_format=request.param[2],
                runtime="python",
                runtime_version=platform.python_version(),
            ),
            dependency_artifacts=[],
            code_artifacts=None,
        ),
    )

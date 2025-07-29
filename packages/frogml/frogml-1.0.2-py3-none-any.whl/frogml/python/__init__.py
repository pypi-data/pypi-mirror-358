import logging
import os.path
import tempfile
from functools import partial
from platform import python_version
from typing import Dict, List, Optional, Any

import cloudpickle
from frogml_core.exceptions import FrogmlException
from frogml_core.utils.proto_utils import PYTHON_FRAMEWORK_FORMAT

from frogml.utils.error_handling import handle_exception
from frogml.utils.files_tools import _get_full_model_path
from frogml.utils.storage import (
    _log_model,
    _download_model_version_from_artifactory,
    _get_model_info_from_artifactory,
)
from frogml.utils.storage_helper import (
    _get_model_framework,
    _get_model_serialization_format,
    _get_model_framework_version,
)
from frogml.utils.validations import _validate_load_model, _validate_typed_log_model

_logger = logging.getLogger(__name__)

_PYTHON_MODEL_FLAVOR = "python"


def log_model(
    function,
    model_name: str,
    repository: str,
    version: Optional[str] = None,
    properties: Optional[Dict[str, str]] = None,
    dependencies: Optional[List[str]] = None,
    code_dir: Optional[str] = None,
    parameters: Optional[Dict[str, Any]] = None,
    metrics: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Log model to a repository in Artifactory.
    :param function: Regressor function to be logged
    :param model_name: Name of the model
    :param repository: Repository to log the model to
    :param version: Version of the model
    :param properties: Model properties
    :param dependencies: Model dependencies path
    :param code_dir: Model code directory path
    :param parameters: Model parameters
    :param metrics: Model metrics
    :return: None
    """

    _logger.info(f"Logging model {model_name} to {repository}")

    _validate_typed_log_model(
        repository=repository,
        model_name=model_name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
        parameters=parameters,
        metrics=metrics,
    )

    with tempfile.TemporaryDirectory() as target_dir:
        full_model_path = _get_full_model_path(
            target_dir=target_dir,
            model_name=model_name,
            serialized_type=PYTHON_FRAMEWORK_FORMAT,
        )

        with open(full_model_path, "wb") as model_file:
            cloudpickle.dump(function, model_file)

        try:
            _log_model(
                model_name=model_name,
                target_dir=target_dir,
                model_flavor=_PYTHON_MODEL_FLAVOR,
                framework_version=python_version(),
                full_model_path=full_model_path,
                serialization_format=PYTHON_FRAMEWORK_FORMAT,
                repository=repository,
                version=version,
                properties=properties,
                dependencies=dependencies,
                code_dir=code_dir,
                parameters=parameters,
                metrics=metrics,
            )
        except Exception as e:
            handle_exception(e, model_name, repository)


def load_model(repository: str, model_name: str, version: str):
    """
    Load model from Artifactory.
    :param repository: Repository to load the model from
    :param model_name: Name of the model
    :param version: Version of the model
    :return: Python function
    """

    _logger.info(f"Loading model {model_name} from {repository}")

    model_info = get_model_info(
        repository=repository, model_name=model_name, version=version
    )
    model_framework = _get_model_framework(model_info)
    serialization_format = _get_model_serialization_format(model_info)

    _validate_load_model(
        repository=repository,
        model_name=model_name,
        version=version,
        model_framework=model_framework,
        model_flavor=_PYTHON_MODEL_FLAVOR,
    )
    with tempfile.TemporaryDirectory() as download_target_path:
        model_path = os.path.join(
            download_target_path, f"{model_name}.{serialization_format}"
        )

        def deserializer_model(full_model_path):
            with open(full_model_path, "rb") as model_file:
                python_model = cloudpickle.load(model_file)
            return python_model

        try:
            return _download_model_version_from_artifactory(
                model_flavor=_PYTHON_MODEL_FLAVOR,
                repository=repository,
                model_name=model_name,
                version=version,
                model_framework=model_framework,
                download_target_path=download_target_path,
                deserializer=partial(deserializer_model, model_path),
            )

        except Exception as e:
            framework_runtime_version = _get_model_framework_version(model_info)
            logging.error(
                f"Failed to load Model. Model was serialized with Python version: {framework_runtime_version}"
            )
            raise FrogmlException(f"Failed to deserialized model: {e}")


def get_model_info(repository: str, model_name: str, version: str) -> Dict:
    """
    Get model information
    :param repository:
    :param model_name:
    :param version:
    :return: Model information
    """

    _logger.info(f"Getting model {model_name} information from {repository}")
    return _get_model_info_from_artifactory(
        repository=repository,
        model_name=model_name,
        version=version,
    )

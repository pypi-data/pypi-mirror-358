.. _models:

Model Types
===================================

This document covers the various model types supported by the FrogML SDK. Currently, only file-based models are supported. Below are the sections detailing each model type and their supported functions.

File-based Models
-----------------

The FrogML SDK currently supports managing file-based models. The following functions are available for this model type:

log_model
#########

Logs a file-based model to Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["pandas==1.2.3"]
    code_dir = "full/path/to/code/dir"
    full_source_path = "/full/path/to/serialized/model.type"

    frogml.files.log_model(
        source_path=full_source_path,
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Downloads a file-based model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path"

    frogml.files.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

get_model_info
##############
Retrieves information about a file-based model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.files.get_model_info(
        repository=repository,
        model_name=name,
        version=version,
    )

CatBoost
-----------
Catboost model to Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["path/to/dependencies/pyproject.toml", "path/to/dependencies/poetry.lock"]
    code_dir = "full/path/to/code/dir"
    catboost_model = get_catboost_model() # Function that Returns a CatBoost model

    frogml.catboost.log_model(
        model=catboost_model,
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Downloads catboost model from Artifactory and return deserialized catboost model.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path"

    catboost_deserialized_model = frogml.catboost.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

get_model_info
##############
Retrieves information about a catboost model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.catboost.get_model_info(
        repository=repository,
        name=name,
        version=version,
    )

Hugging Face
-------------------
Hugging face model to Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["path/to/dependencies/conda.yaml"]
    code_dir = "full/path/to/code/dir"
    model = get_huggingface_model() # Function that Returns a huggingface model
    tokenizer = get_huggingface_tokenizer() # Function that Returns a huggingface tokenizer

    frogml.huggingface.log_model(
        model=model,
        tokenizer=tokenizer,
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Downloads catboost model from Artifactory and return deserialized huggingface model.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path"

    huggingface_deserialized_model = frogml.huggingface.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

get_model_info
##############
Retrieves information about a huggingface model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.huggingface.get_model_info(
        repository=repository,
        name=name,
        version=version,
    )

ONNX
-----------

Onnx model to Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["path/to/dependencies/pyproject.toml", "path/to/dependencies/poetry.lock"]
    code_dir = "full/path/to/code/dir"
    onnx_model = get_onnx_model() # Function that Returns a onnx model

    frogml.onnx.log_model(
        model=onnx_model,
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Downloads onnx model from Artifactory and return deserialized onnx model.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path"

    onnx_deserialized_model = frogml.onnx.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

get_model_info
##############
Retrieves information about a onnx model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.onnx.get_model_info(
        repository=repository,
        name=name,
        version=version,
    )

Scikit-Learn
-------------------
Scikit-Learn model to Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["path/to/dependencies/pyproject.toml", "path/to/dependencies/poetry.lock"]
    code_dir = "full/path/to/code/dir"
    onnx_model = get_scikit_learn() # Function that Returns a scikit learn model

    frogml.scikit_learn.log_model(
        model=onnx_model,
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Downloads onnx model from Artifactory and return deserialized scikit learn model.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path"

    scikit_learn_deserialized_model = frogml.scikit_learn.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

get_model_info
##############
Retrieves information about a scikit learn model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.onnx.get_model_info(
        repository=repository,
        name=name,
        version=version,
    )



Generic Python Function
-----------------------
log_model
#########

Logs a python function model to Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["pandas==1.2.3"]
    code_dir = "full/path/to/code/dir"

    def simple_regression(x, y):
        """
        Perform simple linear regression on the given data.

        :param x: List of input values (independent variable)
        :param y: List of output values (dependent variable)
        :return: Tuple containing the slope and intercept of the regression line
        """
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n

        # Calculate the slope (m) and intercept (b)
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        slope = numerator / denominator
        intercept = mean_y - slope * mean_x

        return slope, intercept

    frogml.python.log_model(
        function=simple_regression,
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Load a python function model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path" # optional parameter

    regression_func = frogml.python.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

get_model_info
##############
Retrieves information about a python function model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.python.get_model_info(
        repository=repository,
        name=name,
        version=version,
    )

PyTorch
--------------
log_model
#########

Logs a Pytorch model to Artifactory.

.. code-block:: python

    import frogml
    import torch.nn as nn

    repository = "repository-name"
    name = "model-name"
    version = "version-1"
    properties = {"key1": "value1"}
    dependencies = ["pandas==1.2.3"]
    code_dir = "full/path/to/code/dir"

    class Classifier(nn.Module):
        def __init__(self):
            super().__init__()
            self.hidden1 = nn.Linear(8, 12)
            self.act1 = nn.ReLU()
            self.hidden2 = nn.Linear(12, 8)
            self.act2 = nn.ReLU()
            self.output = nn.Linear(8, 1)
            self.act_output = nn.Sigmoid()

        def forward(self, x):
            x = self.act1(self.hidden1(x))
            x = self.act2(self.hidden2(x))
            x = self.act_output(self.output(x))
            return x

    frogml.pytorch.log_model(
        model=Classifier(),
        repository=repository,
        model_name=name,
        version=version,
        properties=properties,
        dependencies=dependencies,
        code_dir=code_dir,
    )

load_model
##########

Load a Pytorch model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    model = frogml.pytorch.load_model(
        repository=repository,
        model_name=name,
        version=version,
    )

get_model_info
##############
Retrieves information about a pytorch model from Artifactory.

.. code-block:: python

    import frogml

    repository = "repository-name"
    name = "model-name"
    version = "version-1"

    frogml.pytorch.get_model_info(
        repository=repository,
        name=name,
        version=version,
    )

Quickstart
======================

This guide provides an overview of using FrogML for ML model and dataset management, including how to upload, download, and manage models with JFrog Artifactory.

Authenticating FrogML
---------------------

To use FrogML with Artifactory, you need to authenticate the FrogML client against Artifactory.
Currently, FrogML supports login via environment variables only.

Login via Environment Variables
###############################

You can authenticate the FrogML client using the following environment variables:

- **JF_URL**: Your JFrog platform domain (e.g., ``http://myorg.jfrog.io``)
- **JF_ACCESS_TOKEN**: Your Artifactory token for this domain. To generate a token, log in to Artifactory, navigate to your FrogML repository, and click on "Set Me Up."

Once these environment variables are set, you can log in and start using FrogML.

Uploading Models to Artifactory
-------------------------------

You can upload a model to a FrogML repository using the FrogML SDK.
Currently, FrogML supports file-type models only.
You can upload a model with specified versions, properties, dependencies, and code archives.
This function uses checksum upload, assigning a SHA-2 value to each model. If the binary content cannot be reused, a regular upload occurs.

After uploading, FrogML generates a file named `model-info.json` containing the model name, files, and dependencies.

Example Upload
##############
.. code-block:: python

    import frogml

    repository = "repository-name"
    model_name = "model-name"
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

Supported Dependency Types:

1. ``requirements.txt``
2. ``poetry``
3. ``conda``
4. Explicit versions (e.g., ``dependencies = ["pandas==1.2.3", "numpy==1.2.3"]``)

Downloading Models from Artifactory
-----------------------------------

The following example shows how to download a model from Artifactory using the FrogML SDK:

.. code-block:: python

    import frogml

    repository = "repository-name"
    model_name = "model-name"
    version = "version-1"
    full_target_path = "full/path/to/target/path"

    frogml.files.load_model(
        repository=repository,
        model_name=name,
        version=version,
        target_path=full_target_path,
    )

.. note::
    Dependencies and code archives cannot be downloaded.

Retrieving Model Information
-------------------------------------------

You may retrieve only the relevant model information from Artifactory without downloading the model file:

.. code-block:: python

    import frogml

    repository = "repository-name"
    model_name = "model-name"
    version = "version-1"

    frogml.files.get_model_info(
        repository=repository,
        model_name=name,
        version=version
    )


# Frog ML SDK (FrogML)

## Table of Contents

- [Overview](#overview)
- [Working with FrogML](#working-with-frogml)
   - [Login via Environment Variables](#login-via-environment-variables)
- [Upload ML Model to Artifactory](#upload-ml-model-to-artifactory)
- [Download ML Model from Artifactory](#download-ml-model-from-artifactory)
- [Download Model Information from Artifactory](#download-model-information-from-artifactory)
- [Testing](#testing)
  - [Locally Run Integration Tests Using Artifactory](#locally-run-integration-tests-using-artifactory)
- [Linters](#linters)
  - [Fix Spaces and Line Breaks With](#fix-spaces-and-line-breaks-with)
  - [Fix Formatting With](#fix-formatting-with)

## Overview

FrogML is a powerful and flexible Python library designed to provide advanced ML model and dataset management capabilities by seamlessly integrating JFrog Artifactory as the primary model store and leveraging the JFrog ML Platform.

## Working with FrogML

To use FrogML with Artifactory, authenticate the FrogML client against Artifactory. Currently, FrogML supports login via environment variables only.

The credentials retrieval order is as follows:
1. [Login via Environment Variables](#login-via-environment-variables)

### Login via Environment Variables

You can authenticate the FrogML client using the following environment variables:

- `JF_URL` - Your JFrog platform domain, e.g., `http://myorg.jfrog.io`
- `JF_ACCESS_TOKEN` - Your Artifactory token for this domain. To generate a token, log in to Artifactory, navigate to your FrogML repository, and click "Set Me Up."

After setting these environment variables, you can log in and use FrogML.

## Upload ML Model to Artifactory

You can upload a model to a FrogML repository using FrogML.
Currently, FrogML supports file-type models only. You can upload a model with a specified version, properties, dependencies, and code archive.
This function uses checksum upload, assigning a SHA-2 value to each model for retrieval from storage. If the binary content cannot be reused, the smart upload mechanism performs a regular upload instead.
After uploading the model, FrogML generates a file named `model-info.json` that contains the model name and its related files and dependencies.

The `version` parameter is optional. If not specified, Artifactory will set the version as the timestamp at upload time in UTC format: `yyyy-MM-dd-HH-mm-ss`.
Additionally, you can add properties to the model in Artifactory to categorize and label it.
The function `upload_model_version` returns an instance of `FrogMlModelVersion`, which includes the model's name, and version.

The following example shows how to upload a model to Artifactory:

> **Note**
> The parameters `version`, `properties`, `dependencies`, and `code_dir` are optional.

Upload a model with a specified version, properties, dependencies, and code directory:

```python
import frogml

repository = "repository-name"
name = "model-name"
version = "version-1"
properties = {"key1": "value1"}
dependencies = ["pandas==1.2.3"]
code_dir = "full/path/to/code/dir"
full_source_path = "/full/path/to/serialized/model.type"
frogml.files.log_model(source_path=full_source_path, repository=repository, model_name=name, version=version,
                       properties=properties, dependencies=dependencies, code_dir=code_dir)
```

**Dependencies**

FrogML SDK supports four types of dependencies:
1. `requirements.txt`
2. `poetry`
3. `conda`
4. Explicit versions

To use `requirements.txt`, `conda`, or `poetry`, the `dependencies` parameter should be a list of strings, each representing the path to the file.
For explicit versions, each string should represent a package. For example:

```python
dependencies = ["pandas==1.2.3", "numpy==1.2.3"]
```

## Download ML Model from Artifactory

The example below shows how to download a model from Artifactory using the FrogML SDK:

```python
import frogml

repository = "repository-name"
name = "model-name"
version = "version-1"
full_target_path = "full/path/to/target/path"

frogml.files.load_model(repository=repository, model_name=name, version=version, target_path=full_target_path)
```

> **Note**
> Dependencies and code archives cannot be downloaded.

## Download Model Information from Artifactory

The example below shows how to download model information from Artifactory using the FrogML SDK:

```python
import frogml

repository = "repository-name"
name = "model-name"
version = "version-1"

frogml.files.get_model_info(repository=repository, model_name=name, version=version)
```

## Testing

### Locally Run Unit Tests

To run integration tests locally with Artifactory, use the command:

```bash
make test
```

#### Run Integration Tests Using remote Artifactory

```bash
make integration-test base-url=<remote-artifactory-base-url>
```

### Locally Run Integration Tests

To run integration tests locally with Artifactory, use the command:

currently local image is not available out of the box. so inorder to use it:
1. need to have access to the repo21
2. once the image is up and running:
   1. Open the Artifactory's UI and inject license (at top of the screen you'll have a yellow banner)
   2.  Check the box: "Enable Token Generation via API" in the Administration > Security > General section

```bash
make integration-test --
```

## Linters

### Fix Spaces and Line Breaks With
```
make lint
```

### Fix Formatting With
```
make format
```

import logging
import os
import subprocess
import time
from datetime import timedelta
from typing import Optional, Iterator, Dict, Any

import pytest
import requests
from _pytest.fixtures import fixture
from dotenv import load_dotenv
from podman import PodmanClient
from podman.domain.containers import Container
from podman.errors import PodmanError
from requests import Response
from requests.auth import HTTPBasicAuth
from requests.status_codes import codes

load_dotenv()

logger = logging.getLogger(__name__)


@fixture(scope="session")
def podman_cli() -> str:
    args = ["which", "podman"]
    command = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = command.communicate()
    return stdout.splitlines()[0].decode()


@fixture(scope="session")
def podman_socket(podman_cli: str) -> str:
    args = [
        podman_cli,
        "machine",
        "inspect",
        "--format",
        "{{.ConnectionInfo.PodmanSocket.Path}}",
    ]
    command = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = command.communicate()

    return stdout.splitlines()[0].decode()


@fixture(scope="session")
def artifactory_port() -> int:
    return 8072


@fixture(scope="session")
def artifactory_url(artifactory_port: int) -> str:
    return os.getenv("TEST_BASE_URL", f"http://localhost:{artifactory_port}")


@fixture(scope="session")
def username() -> str:
    return "admin"


@fixture(scope="session")
def password() -> str:
    return "password"


@fixture(scope="session")
def artifactory_api_token(
    artifactory_container: Optional[Container],
    artifactory_url: str,
    username: str,
    password: str,
) -> Optional[str]:
    """
    Generates an API token for JFrog Artifactory using username and password.

    :param artifactory_container: Podman container running Artifactory.
    :param artifactory_url: Base URL of the Artifactory instance (e.g., 'https://qa.jfrog.io/artifactory').
    :param username: Artifactory username.
    :param password: Artifactory password.
    :return: The API token if successful, None otherwise.
    """
    url: str = f"{artifactory_url}/access/api/v1/tokens"
    headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
    data: Dict[str, str] = {
        "username": username,
        "password": password,
        "scope": "applied-permissions/user",
        "token_type": "access_token",
    }

    response: Response = requests.post(
        url, headers=headers, data=data, auth=HTTPBasicAuth(username, password)
    )
    response.raise_for_status()

    token_info: Dict[str, Any] = response.json()
    logger.info(f"API Token generated successfully: {token_info}")

    return token_info.get("access_token")


@pytest.fixture(scope="session")
def artifactory_container(
    podman_socket: str, artifactory_port: int, artifactory_url: str
) -> Iterator[Optional[Container]]:
    """
    Pulls the Podman image and runs a container with the specified configuration.
    Tears down the container after the test session.
    """
    logger.info("Podman image specified. Going to work with local Artifactory.")
    image: str = "qa.jfrog.io/jfrog/artifactory-pro:7.101.0"
    container: Optional[Container] = None

    with PodmanClient(base_url=f"unix://{podman_socket}") as client:
        if not client.ping():
            raise RuntimeError("Podman service is not running.")

        try:
            # Run the Podman container
            logger.info("Starting Podman container...")
            container = client.containers.run(
                image,
                detach=True,
                ports={"8082": artifactory_port},
                environment={
                    "JAVA_OPTS": "-Dstaging.mode=true",
                    "JF_SHARED_DATABASE_ALLOWNONPOSTGRESQL": "true",
                },
            )

            logger.info("Artifactory container is starting...")
            __wait_for_artifactory(artifactory_url)
            logger.info("Artifactory container is ready.")
            yield container

        except PodmanError as e:
            pytest.fail(f"Podman operation failed: {e}")

        finally:
            # Cleanup: Stop and remove the container
            if container:
                logger.info("Stopping and removing Artifactory container...")
                container.stop()
                container.remove(v=True, force=True)


@fixture(scope="session", autouse=True)
def prepare_environment(
    artifactory_url: str,
    jf_project: str,
    repository_in_project: str,
    repository_not_in_project: str,
    artifactory_api_token: Optional[str],
):
    """
    Creates a local repository in Artifactory.

    :param artifactory_url: Base URL of the Artifactory instance (e.g., 'https://qa.jfrog.io/artifactory')
    :param jf_project: Name of the project to create
    :param repository_in_project: Name of the repository to create in a project
    :param repository_not_in_project: Name of the repository to create not in a project
    :param artifactory_api_token: API token for Artifactory
    """

    try:
        os.environ["JF_URL"] = artifactory_url
        os.environ["JF_ACCESS_TOKEN"] = artifactory_api_token
        __install_license(artifactory_url, artifactory_api_token)
        __create_project(artifactory_api_token, artifactory_url, jf_project)
        __create_repository_in_artifactory(
            artifactory_api_token,
            artifactory_url,
            repository_in_project,
            project_name=jf_project,
        )
        __create_repository_in_artifactory(
            artifactory_api_token,
            artifactory_url,
            repository_not_in_project,
        )

    except requests.RequestException as e:
        logger.error(f"An error occurred: {e}")


def __wait_for_artifactory(artifactory_url: str):
    url: str = f"{artifactory_url}/router/api/v1/system/health"

    for _ in range(timedelta(minutes=2).seconds):
        try:
            response: Response = requests.get(url)

            if response.status_code // 100 == 2:
                time.sleep(2)
                break
        except requests.RequestException:
            logger.info("Artifactory is not ready yet. Waiting...")
        time.sleep(1)


def __create_project(api_token: str, base_url: str, jf_project: str):
    url: str = f"{base_url}/access/api/v1/projects"
    data: Dict[str, str] = {
        "display_name": jf_project,
        "description": "The binary repository manager",
        "admin_privileges": {
            "manage_members": True,
            "manage_resources": True,
            "index_resources": True,
        },
        "storage_quota_bytes": 1073741824,
        "project_key": jf_project,
    }
    headers: Dict[str, str] = {
        "authorization": f"Bearer {api_token}",
    }

    logger.info("Creating Project %s...", jf_project)
    response: Response = requests.post(url, headers=headers, json=data)

    if response.status_code in {codes.get("OK"), codes.get("CREATED")}:
        logger.info("Project %s created successfully.", jf_project)
    else:
        logger.error("Failed to create project. Status Code: %s", response.status_code)
        logger.error("Response: %s", response.text)


def __create_repository_in_artifactory(
    api_key: str,
    base_url: str,
    repository_name: str,
    project_name: Optional[str] = None,
):
    """This function creates a repository in Artifactory.

    :param api_key: Artifactory API key
    :param base_url: Base URL of the Artifactory instance
    :param repository_name: Name of the repository to create
    :param project_name: The name of the project to create (if None then the repo won't be associated with any project)
    """
    url: str = f"{base_url}/artifactory/api/repositories/{repository_name}"
    data: Dict[str, str] = {
        "rclass": "local",
        "packageType": "MachineLearning",
        "repoLayoutRef": "simple-default",
    }

    if project_name:
        data["projectKey"] = project_name

    logger.info("Creating local repository %s in Artifactory...", repository_name)
    response: Response = requests.put(
        url, headers={"authorization": f"Bearer {api_key}"}, json=data
    )

    if response.status_code in {codes.get("OK"), codes.get("CREATED")}:
        logger.info("Repositories created successfully.")
    else:
        logger.error(
            f"Failed to create repository. Status Code: {response.status_code}"
        )
        logger.error(f"Response: {response.text}")


def __install_license(base_url: str, api_token: str):
    url: str = f"{base_url}/api/system/licenses"
    data: Dict[str, str] = {
        "licenseKey": os.environ["ARTIFACTORY_LICENSE"],
    }
    headers: Dict[str, str] = {
        "authorization": f"Bearer {api_token}",
    }

    logger.info("Installing license")
    response: Response = requests.post(url, headers=headers, json=data)

    if response.status_code in {codes.get("OK"), codes.get("CREATED")}:
        logger.info("License %s installed successfully.")
    else:
        logger.error("Failed to install license. Status Code: %s", response.status_code)
        logger.error("Response: %s", response.text)

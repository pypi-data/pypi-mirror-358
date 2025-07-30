#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the Environment API client."""

import requests
from ibm_watsonx_data_integration.common.constants import PROD_BASE_URL
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ENVIRONMENT_API_VERSION = 1  # Adjust the version number as needed


# Assisted by watsonx Code Assistant
class EnvironmentApiClient(BaseAPIClient):
    """The API client of the Environment service."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = PROD_BASE_URL,
    ) -> None:
        """The __init__ of the EnvironmentApiClient.

        Args:
            auth: The Authentication object.
            base_url: The Cloud Pak for Data URL. Default: "https://api.dataplatform.cloud.ibm.com"
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path_sset_env = f"sset/engine_manager/v{DEFAULT_ENVIRONMENT_API_VERSION}/streamsets_environments"
        self.url_path_sset_engine_versions = (
            f"sset/engine_manager/v{DEFAULT_ENVIRONMENT_API_VERSION}/streamsets_engine_versions"
        )

    def get_environment(self, env_id: str, params: dict) -> requests.Response:
        """Get a StreamSets Environment by ID.

        Args:
            env_id: Environment asset_id.
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}/{env_id}"
        response = self.get(url=url, params=params)
        return response

    def delete_environment(self, env_id: str, params: dict) -> requests.Response:
        """Deletes an environment by its ID.

        Args:
            env_id: Environment asset_id.
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}/{env_id}"
        response = self.delete(url=url, params=params)
        return response

    def patch_environment(self, data: str, env_id: str, params: dict) -> requests.Response:
        """Updates an existing environment with patch option.

        Args:
            data: List of patch operation to do on an environment.
            env_id: Environment asset_id.
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}/{env_id}"
        response = self.patch(
            url=url, data=data, params=params, headers={"Content-Type": "application/json-patch+json"}
        )
        return response

    def get_environments(self, params: dict) -> requests.Response:
        """Retrieves a list of all environments.

        Args:
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}"
        response = self.get(url=url, params=params)
        return response

    def create_environment(self, data: str, params: dict) -> requests.Response:
        """Creates a new environment.

        Args:
            data: Payload required to create new Environment.
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}"
        response = self.post(url=url, data=data, params=params)
        return response

    def get_docker_run_command(self, env_id: str, params: dict) -> requests.Response:
        """Get the Docker run command for a StreamSets Engine in a StreamSets Environment.

        Args:
            env_id: Environment asset_id.
            params: Query parameters.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}/{env_id}/engine_docker_run_command"
        response = self.get(url=url, params=params, headers={"Accept": "text/plain"})
        return response

    def get_engines(self, env_id: str, params: dict) -> requests.Response:
        """Lists all StreamSets Engines in a StreamSets Environment.

        Args:
            env_id: Environment asset_id.
            params: Query parameters.

        Returns:
            Response from the API.
        """
        url = f"{self.base_url}/{self.url_path_sset_env}/{env_id}/engines"
        response = self.get(url=url, params=params)
        return response

    def get_engine_versions(self) -> requests.Response:
        """List all StreamSets Engine Versions.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_engine_versions}"
        response = self.get(url=url)
        return response

    def get_engine_by_version(self, engine_version: str) -> requests.Response:
        """Get a StreamSets Engine info by via version name.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path_sset_engine_versions}/{engine_version}"
        response = self.get(url=url)
        return response

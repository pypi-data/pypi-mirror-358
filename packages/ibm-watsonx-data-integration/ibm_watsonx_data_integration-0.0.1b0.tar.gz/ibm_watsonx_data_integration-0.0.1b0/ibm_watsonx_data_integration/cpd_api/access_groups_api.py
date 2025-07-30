# IBM Confidential
# PID 5900-BAF
# Copyright StreamSets Inc., an IBM Company 2025

"""This module containing the AccessGroupsAPIClient class."""

import requests
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_ACCESS_GROUP_API_VERSION = 2


class AccessGroupsAPIClient(BaseAPIClient):
    """The API Client of Access Groups."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_url: str = "https://iam.cloud.ibm.com",
    ) -> None:
        """Initializes the AccessGroupsAPIClient.

        Args:
            auth: The Authentication object.
            base_url: Default is "https://iam.cloud.ibm.com".
        """
        super().__init__(auth=auth, base_url=base_url)
        self.url_path = f"v{DEFAULT_ACCESS_GROUP_API_VERSION}/groups"

    def get_access_group(self, access_group_id: str) -> requests.Response:
        """Gets an access group.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}"
        response = self.get(url=url)
        return response

    def get_all_access_groups(self, account_id: str) -> requests.Response:
        """Lists all access groups under an account. Will only list those the listed user can access.

        Args:
            account_id: The account ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        params = {"account_id": account_id}
        response = self.get(url=url, params=params)
        return response

    def create_access_group(self, account_id: str = None, data: dict = None) -> requests.Response:
        """Creates a new access group.

        Args:
            account_id: The account ID.
            data: The name and description of the access group to be created/updated, in json form.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}"
        params = {"account_id": account_id}
        response = self.post(url=url, params=params, data=data)
        return response

    def update_access_group(self, access_group_id: str, etag: str, data: dict) -> requests.Response:
        """Updates existing access group.

        Args:
            access_group_id: The access group ID.
            etag: The etag for the latest revision to the AccessGroup.
            data: The name and description of the access group to be created/updated, in json form.

        Returns:
            A HTTP response.
        """
        headers = {"If-Match": etag}

        url = f"{self.base_url}/{self.url_path}/{access_group_id}"
        response = self.patch(url=url, data=data, headers=headers)
        return response

    def delete_access_group(self, access_group_id: str) -> requests.Response:
        """Deletes an access group from an account.

        Args:
            access_group_id: The access group ID.

        Returns:
            A HTTP response.
        """
        url = f"{self.base_url}/{self.url_path}/{access_group_id}"
        response = self.delete(url=url)
        return response

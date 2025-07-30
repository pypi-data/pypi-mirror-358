#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing the SDC API client."""

import json
import requests
import urllib.parse
import urllib3
from ibm_watsonx_data_integration.common.utils import wait_and_retry_on_http_error
from ibm_watsonx_data_integration.cpd_api.base import BaseAPIClient
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator

DEFAULT_SDC_API_VERSION = 1
REQUIRED_HEADERS = {"X-Requested-By": "sdc", "X-SS-REST-CALL": "true", "content-type": "application/json"}


class DataCollectorAPIClient(BaseAPIClient):
    """The API Client of the Data Collector."""

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        engine_url: str,
    ) -> None:
        """The __init__ of the EngineApiClient.

        Args:
            auth: The Authentication object.
            engine_url: The URL of the engine.
        """
        super().__init__(auth=auth, base_url=engine_url)
        self.url = f"{self.base_url}/rest/v{DEFAULT_SDC_API_VERSION}"

        # As of now, sdc uses a self-signed certificate from the machine it is running in.
        # It is impossible to make calls to the sdc without being on that machine ourselves,
        # this will be a known issue till we have tunneling set up.
        # requests made through this class will make it requests without verification
        # ToDo: WSDK-210
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    @wait_and_retry_on_http_error
    def create_pipeline(self, pipeline_title: str, params: dict[str, Any] | None = None) -> requests.Response:
        """Create a pipeline in a Datacollector."""
        url = f"{self.url}/pipeline/{urllib.parse.quote(pipeline_title)}"
        return self.put(url=url, params=params, headers=REQUIRED_HEADERS, verify=False)

    @wait_and_retry_on_http_error
    def update_pipeline(self, pipeline_id: str, pipeline_definition: dict) -> requests.Response:
        """Update a pipeline in a Datacollector."""
        url = f"{self.url}/pipeline/{pipeline_id}"
        return self.post(url=url, data=json.dumps(pipeline_definition), headers=REQUIRED_HEADERS, verify=False)

    @wait_and_retry_on_http_error
    def get_pipeline_by_id(self, pipeline_id: str) -> requests.Response:
        """Get a pipeline in a DataCollector."""
        url = f"{self.url}/pipeline/{pipeline_id}"
        return self.get(url=url, headers=REQUIRED_HEADERS, verify=False)

    @wait_and_retry_on_http_error
    def delete_pipeline(self, pipeline_id: str) -> requests.Response:
        """Delete a pipeline in a Datacollector."""
        url = f"{self.url}/pipeline/{pipeline_id}"
        return self.delete(url=url, headers=REQUIRED_HEADERS, verify=False)

    @wait_and_retry_on_http_error
    def get_library_definitions(self) -> requests.Response:
        """Get the library definitions of an engine."""
        url = f"{self.url}/definitions"
        return self.get(url=url, verify=False)

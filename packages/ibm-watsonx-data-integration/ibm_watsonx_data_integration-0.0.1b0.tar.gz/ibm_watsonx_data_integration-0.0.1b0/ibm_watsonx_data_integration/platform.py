#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""This module defines top-level abstractions for WatsonX Data Integration."""

import json
import logging
import requests
from ibm_watsonx_data_integration.common.constants import (
    ACCOUNT_MANAGEMENT_URL,
    DEFAULT_RESOURCE_REGION_ID_MAP,
    GLOBAL_CATALOG_URL,
    IAM_URL,
    PROD_BASE_URL,
    RESOURCE_CONTROLLER_URL,
    RESOURCE_PLAN_ID_MAP,
    USER_MANAGEMENT_URL,
)
from ibm_watsonx_data_integration.common.utils import _get_service_id_to_name_map
from ibm_watsonx_data_integration.cpd_api import (
    AccessGroupsAPIClient,
    AccountAPIClient,
    ConnectionsApiClient,
    EngineApiClient,
    EnvironmentApiClient,
    GlobalCatalogApiClient,
    JobApiClient,
    MeteringApiClient,
    ProjectApiClient,
    ResourceControllerApiClient,
    RoleAPIClient,
    UserAPIClient,
)
from ibm_watsonx_data_integration.cpd_models import (
    AccessGroup,
    Account,
    Accounts,
    ConnectionFile,
    ConnectionFiles,
    ConnectionsServiceInfo,
    DatasourceTypes,
    Project,
    Projects,
    Role,
    Roles,
    RoleType,
    Service,
    Services,
    UserProfile,
    UserProfiles,
)
from ibm_watsonx_data_integration.services.streamsets.api import StreamsetsFlowApiClient
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.common.auth import BaseAuthenticator


logger = logging.getLogger(__name__)


class Platform:
    """Class to interact with IBM Cloud Pak for Data."""

    _account_api: AccountAPIClient
    _resource_controller_api: ResourceControllerApiClient
    _global_catalog_api: GlobalCatalogApiClient
    _project_api: ProjectApiClient
    _job_api: JobApiClient
    _environment_api: EnvironmentApiClient
    _streamsets_flow_api: StreamsetsFlowApiClient
    _user_api: UserAPIClient
    _access_group_api: AccessGroupsAPIClient
    _service_id_to_name_map: dict
    _role_api_client: RoleAPIClient
    _current_account: Account | None

    def __init__(
        self,
        auth: "BaseAuthenticator",  # pragma: allowlist secret
        base_api_url: str = PROD_BASE_URL,
        global_catalog_url: str = GLOBAL_CATALOG_URL,
        resource_controller_url: str = RESOURCE_CONTROLLER_URL,
        account_management_url: str = ACCOUNT_MANAGEMENT_URL,
        user_management_url: str = USER_MANAGEMENT_URL,
        iam_url: str = IAM_URL,
    ) -> None:
        """The __init__ for the Platform class.

        Args:
            auth: The Authentication object.
            base_api_url: The Cloud Pak for Data URL.
            global_catalog_url: Global Catalog URL.
            resource_controller_url: Resource Controller URL.
            account_management_url: Account Management URL.
            user_management_url: User Management URL.
            iam_url: Identity and access management URL.
        """
        self._account_api = AccountAPIClient(auth=auth, base_url=account_management_url)
        self._resource_controller_api = ResourceControllerApiClient(auth=auth, base_url=resource_controller_url)
        self._global_catalog_api = GlobalCatalogApiClient(auth=auth, base_url=global_catalog_url)
        self._project_api = ProjectApiClient(auth=auth, base_url=base_api_url)
        self._job_api = JobApiClient(auth=auth, base_url=base_api_url)
        self._environment_api = EnvironmentApiClient(auth=auth, base_url=base_api_url)
        self._streamsets_flow_api = StreamsetsFlowApiClient(auth=auth, base_url=base_api_url)
        self._user_api = UserAPIClient(auth=auth, base_url=user_management_url)
        self._access_group_api = AccessGroupsAPIClient(auth=auth, base_url=iam_url)
        self._engine_api = EngineApiClient(auth=auth, base_url=base_api_url)
        self._connections_api = ConnectionsApiClient(auth=auth, base_url=base_api_url)
        self._metering_api = MeteringApiClient(auth=auth, base_url=base_api_url)
        self._service_id_to_name_map = _get_service_id_to_name_map(self)
        self._role_api_client = RoleAPIClient(auth=auth, base_url=iam_url)

        self._current_account = None

    @property
    def service_instances(self) -> Services:
        """Returns a list of Service Instances.

        Returns:
            An instance of :py:class:`ibm_watsonx_data_integration.cpd_models.Services`
        """
        return Services(self)

    def create_service_instance(
        self,
        instance_type: str,
        name: str,
        target: str | None = None,
        tags: list | None = None,
    ) -> Service:
        """Creates Service Instance.

        Args:
            instance_type: The Instance Type.
            name: The name of the Instance.
            target: The target of the Instance.
            tags: The tags of the Instance.

        Returns:
            A HTTP response.
        """
        resource_plan_id = RESOURCE_PLAN_ID_MAP[instance_type]
        resource_group_id = self._resource_controller_api.get_resource_groups().json()["resources"][0]["id"]
        target = target if target else DEFAULT_RESOURCE_REGION_ID_MAP[instance_type]
        tags = tags if tags else []

        data = {
            "name": name,
            "target": target,
            "resource_plan_id": resource_plan_id,
            "resource_group": resource_group_id,
            "tags": tags,
        }

        response = self._resource_controller_api.create_resource_instance(json.dumps(data))

        return Service(platform=self, **response.json())

    def delete_service_instance(self, service: Service, delete_keys: bool = True) -> requests.Response:
        """Delete Resource Instance.

        Args:
            service: The Service to delete.
            delete_keys: Whether to recursively delete resource keys.

        Returns:
            A HTTP response.
        """
        return self._resource_controller_api.delete_resource_instance(service.guid, recursive=delete_keys)

    @property
    def projects(self) -> Projects:
        """Returns a list of Project objects.

        Returns:
            An instance of :py:class:`ibm_watsonx_data_integration.cpd_models.Projects`
        """
        return Projects(self)

    def create_project(
        self, name: str, description: str = "", tags: list = None, public: bool = False, project_type: str = "wx"
    ) -> Project:
        """Create a Project.

        Args:
            name: The Project name.
            description: The name of the Project.
            tags: The tags of the Project.
            public: Whether the Project is public.
            project_type: Type of the Project - 'cpd' - IBM Cloud Pak for Data; 'wx' - IBM watsonx (and Data Fabric).

        Returns:
            A project instance.
        """
        cloud_storage_resource = self._resource_controller_api.get_resource_instances(
            {"name": "CloudObjectStorage"}
        ).json()
        if cloud_storage_resource["rows_count"] < 1:
            raise Exception("Cloud Object Storage does not exist. Cannot proceed.")

        data = {
            "name": name,
            "description": description,
            "generator": "watsonx-di-sdk",
            "public": public,
            "tags": ["sdk-tags"] if not tags else tags,
            "storage": {
                "type": "bmcos_object_storage",
                "guid": cloud_storage_resource["resources"][0]["guid"],
                "resource_crn": cloud_storage_resource["resources"][0]["id"],
            },
            "type": project_type,
        }

        response = self._project_api.create_project(json.dumps(data))
        location = response.json()["location"]
        project_id = location.split("/")[-1]

        project_json = self._project_api.get_project(project_id).json()

        return Project(platform=self, **project_json)

    def delete_project(self, project: Project) -> requests.Response:
        """Deletes a Project.

        Args:
            project: The Project to delete.

        Returns:
            A HTTP response.
        """
        return self._project_api.delete_project(project.metadata.guid)

    def update_project(self, project: Project) -> requests.Response:
        """Updates a Project.

        Args:
            project: The Project to delete.

        Returns:
            A HTTP response.
        """
        # Update tags
        project._update_tags()

        # Update rest of project
        data = {"name": project.name, "description": project.description, "public": project.public}

        project_json = project.model_dump()
        if "catalog" in project_json:
            data["catalog"] = {"guid": project_json["catalog"]["guid"], "public": project_json["catalog"]["public"]}

        data = json.dumps(data)
        return self._project_api.update_project(id=project.metadata.guid, data=data)

    @property
    def accounts(self) -> Accounts:
        """Returns a list of all accounts associated with the current IAM identity or API key.

        Returns:
            A list of account objects retrieved from the API.
        """
        return Accounts(self)

    @property
    def current_account(self) -> Account:
        """Gets the current (first) account from the list of accounts.

        Returns:
            An account object representing the first account retrieved from the accounts list.
        """
        if not self._current_account:
            all_accounts = self.accounts
            if not all_accounts:
                raise ValueError("No accounts available for the provided IAM identity or API key.")
            self._current_account = all_accounts[0]
        return self._current_account

    @current_account.setter
    def current_account(self, account: Account) -> None:
        """Override which account will be used for all subsequent calls.

        Args:
            account: The Account object to set as the current account.

        Returns:
            None.
        """
        self._current_account = account

    def get_account(self, account_id: str) -> Account:
        """Retrieves account details for the specified account ID.

        Args:
            account_id: The unique identifier of the account.

        Returns:
            An account containing detailed account information, including metadata and customer details.
        """
        response = self._account_api.get_account(account_id)
        response_json = response.json()
        data = {"entity": response_json.get("entity", {}), "metadata": response_json.get("metadata", {})}
        account_obj = Account(platform=self, **data)
        return account_obj

    @property
    def users(self) -> UserProfiles:
        """Retrieves collection of all the user profiles in the current account.

        Returns:
            An iterable collection of user profiles.
        """
        return UserProfiles(self)

    def get_user_profile(self, iam_id: str) -> UserProfile:
        """Retrieves the user profile details for the specified account and user.

        Args:
            iam_id: The unique identifier (IAM ID) of the user.

        Returns:
            A user profile containing detailed user profile information.
        """
        user_json = self._user_api.get_user_profile(self.current_account.account_id, iam_id).json()
        return UserProfile(platform=self, **user_json)

    @property
    def roles(self) -> Roles:
        """Returns a list of all roles.

        Returns:
            An instance of :py:class:`watsonx_di_sdk.role_model.Roles`
        """
        return Roles(self)

    def create_role(
        self, name: str, display_name: str, service_name: str, actions: list, description: str | None = None
    ) -> Role:
        """Creates a custom role for a specific service within the account.

        Args:
            display_name: The display the name of the role that is shown in the console.
            actions: The actions of the role (list of strings).
            name: The name of the role that is used in the CRN. This must be alphanumeric and capitalized.
            service_name: The service name.
            description: The description of the role.

        Returns:
            A role instance.
        """
        if name and name[0].islower():
            name = name[0].upper() + name[1:]

        data = {
            "name": name,
            "display_name": display_name,
            "account_id": self.current_account.account_id,
            "service_name": service_name,
            "actions": actions,
        }

        if description:
            data["description"] = description

        response = self._role_api_client.create_role(json.dumps(data))
        response_json = response.json()
        response_json["role_type"] = RoleType.CUSTOM_ROLE
        return Role(platform=self, **response_json)

    def update_role(self, role: Role) -> requests.Response:
        """Update a custom role.

        A role administrator might want to update an existing custom role by updating the display name, description, or
        the actions that are mapped to the role. The name, account_id, and service_name can't be changed.

        Args:
            role: The role to update.

        Returns:
            A HTTP response.
        """
        if role.role_type is not RoleType.CUSTOM_ROLE.value:
            raise TypeError("You can only update a custom role.")

        data = {
            "display_name": role.display_name,
            "description": role.description,
            "actions": role.actions,
        }

        if not role.etag:
            role = self.roles.get_all(role_id=role.id)[0]

        return self._role_api_client.update_role(role.id, role.etag, json.dumps(data))

    def delete_role(self, role: Role) -> requests.Response:
        """Delete a custom role.

        Args:
            role: The role to delete.

        Returns:
            A HTTP response.
        """
        if role.role_type is not RoleType.CUSTOM_ROLE.value:
            raise TypeError("You can only delete a custom role.")

        return self._role_api_client.delete_role(role.id)

    @property
    def access_groups(self) -> list[AccessGroup]:
        """Returns a list of AccessGroup objects.

        Returns:
            A collection of Access Group objects retrieved from the API.
        """
        self.current_account

        access_group_json = self._access_group_api.get_all_access_groups(self._current_account.account_id).json()[
            "groups"
        ]
        access_groups = []

        for access_group in access_group_json:
            access_group["account_id"] = self._current_account.account_id
            access_groups.append(AccessGroup(platform=self, **access_group))

        return access_groups

    def create_access_group(self, name: str, description: str | None = None) -> AccessGroup:
        """Creates an access group and returns the created access group object.

        Args:
            name: Name of the Access Group
            description: Description of the Access Group

        Returns:
            An Access Group instance.
        """
        self.current_account

        data = {"name": name, "description": description}
        data = json.dumps(data)

        response = self._access_group_api.create_access_group(self._current_account.account_id, data=data)

        access_group_json = response.json()
        access_group_json["etag"] = response.headers["Etag"]
        return AccessGroup(platform=self, **access_group_json)

    def update_access_group(self, access_group: AccessGroup) -> requests.Response:
        """Updates an existing group and returns the output for api call to update.

        Args:
            access_group: Access Group to be updated

        Returns:
            A HTTP response.
        """
        data = {"name": access_group.name, "description": access_group.description}
        data = json.dumps(data)

        get_ag = self._access_group_api.get_access_group(access_group_id=access_group.id)
        etag = get_ag.headers["Etag"]

        response = self._access_group_api.update_access_group(access_group_id=access_group.id, etag=etag, data=data)

        return response

    def delete_access_group(self, access_group: AccessGroup) -> requests.Response:
        """Deletes an access group and returns output of api call to delete.

        Args:
            access_group: Access Group to be deleted

        Returns:
            A HTTP response.
        """
        return self._access_group_api.delete_access_group(access_group.id)

    @property
    def datasources(self) -> DatasourceTypes:
        """Retrieves available datasource types.

        Returns:
            A list of available DatasourceTypes.
        """
        return DatasourceTypes(platform=self)

    @property
    def connections_service_info(self) -> ConnectionsServiceInfo:
        """Retrieves information about connection service. Can be used as heartheat mechanism.

        Returns:
            A connection service information.
        """
        version = self._connections_api.get_version(params=dict())
        return ConnectionsServiceInfo(**version.json())

    @property
    def files(self) -> ConnectionFiles:
        """Retrieves list of files.

        Returns:
            List of connection files.
        """
        return ConnectionFiles(platform=self)

    def upload_file(self, name: str, file: Path) -> requests.Response:
        """Uploads file.

        Args:
            name: Name of the file to upload.
            file: File to upload.

        Returns:
            A HTTP response.
        """
        if not file.is_file():
            raise ValueError("Incorrect file path provided.")
        if not file.exists():
            raise ValueError("File path does not exists.")

        return self._connections_api.upload_file(file_name=name, file=file)

    def delete_file(self, file: ConnectionFile) -> requests.Response:
        """Delete a file.

        Returns:
            A HTTP response.
        """
        return file._delete()

    @property
    def available_engine_versions(self) -> list[str]:
        """Lists all StreamSets Engine Versions.

        Returns:
            A list of Engine versions.
        """
        response = self._environment_api.get_engine_versions()
        return [data["engine_version_id"] for data in response.json()["streamsets_engine_versions"]]

    def get_engine_version_info(self, engine_version: str) -> dict:
        """Get a StreamSets Engine information.

        Returns:
            A dict with information about engine version.

        Raises:
            HTTPError: If the request fails.
        """
        try:
            return self._environment_api.get_engine_by_version(engine_version=engine_version).json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(
                    "Engine version: %s does not exist. "
                    "Please check available engine versions using platform.available_engine_versions property.",
                    engine_version,
                )
            raise

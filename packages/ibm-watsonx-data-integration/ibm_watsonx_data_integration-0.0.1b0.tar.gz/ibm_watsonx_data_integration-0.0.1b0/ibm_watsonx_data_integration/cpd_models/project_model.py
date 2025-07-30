#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Project Models."""

import json
import requests
from ibm_watsonx_data_integration.common.constants import SUPPORTED_FLOWS
from ibm_watsonx_data_integration.common.json_patch_format import prepare_json_patch_payload
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models import (
    Connection,
    Connections,
    DatasourceType,
    Engine,
    Environment,
    Environments,
    Job,
    Jobs,
)
from ibm_watsonx_data_integration.services.streamsets.models import (
    StreamsetsConnection,
    StreamsetsFlow,
    StreamsetsFlows,
)
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any, ClassVar, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class ProjectMetadata(BaseModel):
    """Model for metadata in a project."""

    guid: str = Field(repr=True)
    url: str = Field(repr=False)
    created_at: str | None = Field(repr=False)
    updated_at: str | None = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class Storage(BaseModel):
    """Model for Storage details in a project."""

    type: str
    guid: str = Field(frozen=True)
    properties: dict[str, Any]
    _expose: bool = PrivateAttr(default=False)


class Scope(BaseModel):
    """Model for Scope details in a project."""

    bss_account_id: str = Field(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class Project(BaseModel):
    """The Model for Projects."""

    metadata: ProjectMetadata = Field(repr=True)

    name: str = Field(repr=True)
    description: str = Field(repr=False)
    type: str | None = Field(repr=False)
    generator: str | None = Field(repr=False)
    public: bool | None = Field(repr=False)
    creator: str | None = Field(repr=False)

    storage: Storage | None = Field(repr=False)
    scope: Scope | None = Field(repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity": {}}

    def __init__(self, platform: Optional["Platform"] = None, **project_json: dict) -> None:
        """The __init__ of the Project class.

        Args:
            platform: The Platform object.
            project_json: The JSON for the Service.
        """
        super().__init__(**project_json)
        self._platform = platform
        self._inital_tags = [] if not hasattr(self, "tags") else list(self.tags)

    def _update_tags(self) -> None:
        """Updates tags of the Project."""
        initial_tags = set(self._inital_tags)
        current_tags = set(self.tags)

        body = []

        tags_to_delete = initial_tags - current_tags
        if tags_to_delete:
            body.append({"op": "remove", "tags": list(tags_to_delete)})

        tags_to_add = current_tags - initial_tags
        if tags_to_add:
            body.append({"op": "add", "tags": list(tags_to_add)})

        if body:
            self._inital_tags = self.tags
            self._platform._project_api.update_tags(self.metadata.guid, json.dumps(body))

    @property
    def jobs(self) -> Jobs:
        """Retrieves jobs associated with the project.

        Returns:
            A list of Jobs within the project.
        """
        return Jobs(platform=self._platform, project=self)

    def create_job(
        self,
        name: str,
        configuration: dict[str, Any],
        description: str,
        job_parameters: dict[str, Any] | None = None,
        retention_policy: dict[str, int] | None = None,
        parameter_sets: list[dict[str, str]] | None = None,
        schedule: str | None = None,
        schedule_info: dict[str, Any] | None = None,
        asset_ref: str | None = None,
        asset_ref_type: str | None = None,
    ) -> Job:
        """Create Job for given asset ref or asset ref type.

        Args:
            name: Name for a Job.
            configuration: Environment variables for a Job.
            description: Job description.
            job_parameters: Parameters use internally by a Job.
            retention_policy: Retention policy for a Job.
            parameter_sets: Parameter sets for a Job.
            schedule: Crone string.
            schedule_info: Schedule infor for a Job.
            asset_ref: Reference to asset based on Job will be created.
            asset_ref_type: Reference to asset type based on Job will be created.

        Returns:
            A Job instance.
        """
        if asset_ref and asset_ref_type:
            raise TypeError("Use asset_ref or asset_ref_type not both!")

        if not (asset_ref or asset_ref_type):
            raise TypeError("Please provide either asset_ref or asset_ret_type to proceed.")

        query_params = {"project_id": self.metadata.guid}

        new_job = {
            "name": name,
            "description": description,
            "asset_ref": asset_ref,
            "asset_ref_type": asset_ref_type,
            "configuration": configuration,
            "schedule": schedule,
        }

        # Remove keys with `None` values, since endpoint does not allow
        # JSON null for fields.
        new_job = {k: v for k, v in new_job.items() if v is not None}

        # json.dumps can not serialize Pydantic models so we must call `model_dump` manually
        if parameter_sets:
            new_job["parameter_sets"] = parameter_sets

        if job_parameters:
            new_job["job_parameters"] = [{"name": k, "value": v} for k, v in job_parameters.items()]

        if retention_policy:
            new_job["retention_policy"] = retention_policy

        if schedule_info:
            new_job["schedule_info"] = schedule_info

        data = {"job": new_job}
        res = self._platform._job_api.create_job(  # noqa
            data=json.dumps(data), params=query_params
        )
        job_json = res.json()
        return Job(platform=self._platform, project=self, **job_json)

    def delete_job(self, job: Job) -> requests.Response:
        """Allows to delete specified Job within project.

        Args:
            job: Instance of a Job to delete.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
        """
        query_params = {"project_id": self.metadata.guid}
        return self._platform._job_api.delete_job(  # noqa
            id=job.metadata.asset_id, params=query_params
        )

    def update_job(self, job: Job) -> requests.Response:
        """Allows to update specified Job within a project.

        Args:
            job: Instance of a Job to update.

        Returns:
            A HTTP response. If it is 200, then the operation completed successfully.
        """
        query_params = {
            "project_id": self.metadata.guid,
        }
        payload = prepare_json_patch_payload(job.origin, job.model_dump())
        return self._platform._job_api.update_job(  # noqa
            id=job.metadata.asset_id, data=payload, params=query_params
        )

    @property
    def environments(self) -> Environments:
        """Retrieves environments associated with the project.

        Returns:
            A list of Environments within the project.
        """
        return Environments(platform=self._platform, project=self)

    def create_environment(
        self,
        *,
        name: str,
        engine_version: str,
        description: str = None,
        engine_type: str = "data_collector",
        engine_properties: dict = None,
        log4j2_properties: dict = None,
        stage_libs: list = None,
        jvm_options: list = None,
        max_cpu_load: int = None,
        max_memory_used: int = None,
        max_flows_running: int = None,
        engine_heartbeat_interval: int = None,
        cpus_to_allocate: int = None,
    ) -> Environment:
        """Allows to create a new Environment within project.

        All of not set parameters will be skipped and set with default values provided by backed.

        Args:
            name: Name of the environment.
            description: Description of the environment.
            engine_type: Type of the engine. Defaults to "DATA_COLLECTOR".
            engine_version: Version of the engine.
            engine_properties: Properties of the engine.
            log4j2_properties: Log4j2 properties.
            stage_libs: Stage libraries.
            jvm_options: JVM options.
            max_cpu_load: Maximum CPU load.
            max_memory_used: Maximum memory used.
            max_flows_running: Maximum flows running.
            engine_heartbeat_interval: Engine heartbeat interval.
            cpus_to_allocate: Number of CPU used.

        Returns:
            The created environment.
        """
        params = locals()
        params.pop("self")

        env_json = {
            "name": params.pop("name"),
            "description": params.pop("description"),
            "streamsets_environment": {k: v for k, v in params.items() if v is not None},
        }
        query_params = {
            "project_id": self.metadata.guid,
        }
        api_response = self._platform._environment_api.create_environment(  # noqa
            data=json.dumps(env_json), params=query_params
        )
        payload = api_response.json()
        payload.pop("asset_id", None)
        return Environment(platform=self._platform, project=self, **payload)

    def get_environment(self, asset_id: str = None) -> Environment:
        """Retrieve an environment by its asset_id.

        Args:
            asset_id: The asset_id of the environment to retrieve.

        Returns:
            The retrieved environment.

        Raises:
            ValueError: If asset_id is not provided.
            HTTPError: If the request fails.
        """
        if not asset_id:
            raise ValueError("asset_id must be provided")
        query_params = {
            "project_id": self.metadata.guid,
        }
        api_response = self._platform._environment_api.get_environment(  # noqa
            env_id=asset_id, params=query_params
        )
        if api_response.status_code != 200:
            raise api_response.raise_for_status()
        return Environment(platform=self._platform, project=self, **api_response.json())

    def delete_environment(self, environment: Environment) -> requests.Response:
        """Allows to delete specified Environment within project.

        Args:
            environment: Instance of an Environment to delete.

        Returns:
            A HTTP response.
        """
        query_params = {"project_id": self.metadata.guid}
        return self._platform._environment_api.delete_environment(  # noqa
            env_id=environment.metadata.asset_id, params=query_params
        )

    def update_environment(self, environment: Environment) -> requests.Response:
        """Allows to update specified Environment within a project.

        Args:
            environment: Instance of an Environment to update.

        Returns:
            A HTTP response.
        """
        query_params = {
            "project_id": self.metadata.guid,
        }
        payload = prepare_json_patch_payload(environment.origin, environment.model_dump())
        return self._platform._environment_api.patch_environment(  # noqa
            env_id=environment.metadata.asset_id, data=payload, params=query_params
        )

    @property
    def flows(self) -> StreamsetsFlows:
        """Returns Flows from the Project."""
        return StreamsetsFlows(project=self)

    def delete_flow(self, flow: StreamsetsFlow) -> requests.Response:
        """Delete a Flow.

        Args:
            flow: The Flow object.

        Returns:
            A HTTP response.
        """
        engine = next(
            engine for engine in self.engines if engine.streamsets_environment_asset_id == flow.environment_id
        )
        engine.api_client.delete_pipeline(pipeline_id=flow.get_executor_id())

        params = {"project_id": self.metadata.guid}
        return self._platform._streamsets_flow_api.delete_streamsets_flow(params=params, flow_id=flow.id)

    def create_flow(
        self, name: str, environment: Environment, description: str = "", flow_type: str = "streamsets"
    ) -> StreamsetsFlow:
        """Creates a Flow.

        Args:
            name: The name of the Streamsets flow.
            environment: The environment which will be used to run this flow.
            description: The description of the Streamsets flow.
            flow_type: The type of flow.

        Returns:
            The Streamsets Flow object.

        Raises:
            TypeError: If flow_type is not supported.
        """
        if flow_type not in SUPPORTED_FLOWS:
            raise TypeError("Flow type not supported")

        if not environment.engines:
            raise ValueError(
                "No engines installed for environment. Install an engine in the environment before creating flows."
            )

        # create a flow in the project
        payload = json.dumps(
            {
                "name": name,
                "description": description,
                "environment_id": environment.metadata.asset_id,
                "engine_version": environment.engine_version,
            }
        )
        params = {"project_id": self.metadata.guid}
        create_flow_response = self._platform._streamsets_flow_api.create_streamsets_flow(params=params, data=payload)
        flow = StreamsetsFlow(project=self, **create_flow_response.json()["flow"])

        # create a pipeline using the flow's asset id and some defaults. this is what the UI does.
        engine = environment.engines[0]
        create_pipeline_response = engine.api_client.create_pipeline(
            pipeline_title=flow.get_executor_id(),
            params=dict(description="description", draft=False, autoGeneratePipelineId=False),
        )

        # add the pipeline definition to the flow
        flow.pipeline_definition = create_pipeline_response.json()
        self.update_flow(flow)

        return flow

    def update_flow(self, flow: StreamsetsFlow) -> requests.Response:
        """Update a Flow.

        Args:
            flow: The Flow object.

        Returns:
            A HTTP response.
        """
        engine = next(
            engine for engine in self.engines if engine.streamsets_environment_asset_id == flow.environment_id
        )
        update_engine_pipeline_response = engine.api_client.update_pipeline(
            pipeline_id=flow.get_executor_id(), pipeline_definition=flow.pipeline_definition
        )

        params = {"project_id": self.metadata.guid}
        payload = {
            "name": flow.name,
            "connection_ids": flow.connection_ids if flow.connection_ids else [],
            "description": flow.description,
            "environment_id": flow.environment_id,
            "engine_version": flow.engine_version,
            "fragment_ids": flow.fragments_ids if flow.fragments_ids else [],
            "pipeline_definition": update_engine_pipeline_response.json(),
        }

        update_flow_response = self._platform._streamsets_flow_api.update_streamsets_flow(
            params=params, flow_id=flow.id, data=json.dumps(payload)
        )
        update_flow_json = update_flow_response.json()
        flow._update(
            project=self,
            pipeline_definition=update_flow_json["pipeline_definition"],
            **update_flow_json["flow"],
        )

        return update_flow_response

    def duplicate_flow(self, flow: StreamsetsFlow, name: str, description: str = "") -> StreamsetsFlow:
        """Duplicate a  Flow.

        Args:
            flow:The Flow.
            name: The name of the Streamsets flow.
            description: The description of the Streamsets flow.

        Returns:
            A copy of passed Streamsets flow.
        """
        payload = json.dumps({"name": name, "description": description})
        params = {"project_id": self.metadata.guid}

        duplicate_flow_response = self._platform._streamsets_flow_api.duplicate_streamsets_flow(
            params=params, data=payload, flow_id=flow.id
        )
        duplicate_flow_response_json = duplicate_flow_response.json()
        duplicate_flow = StreamsetsFlow(
            project=self,
            pipeline_definition=duplicate_flow_response_json["pipeline_definition"],
            **duplicate_flow_response_json["flow"],
        )

        # create the flow on the engine
        environment = next(
            environment for environment in self.environments if environment.metadata.asset_id == flow.environment_id
        )
        engine = environment.engines[0]
        create_pipeline_response = engine.api_client.create_pipeline(
            pipeline_title=duplicate_flow.get_executor_id(),
            params=dict(description=description or "description", draft=False, autoGeneratePipelineId=False),
        )
        created_pipeline_definition = create_pipeline_response.json()

        # update the duplicate flow's pipeline definition's pipeline id, uuid and info, these are set by the engine
        duplicate_flow_pipeline_definition = duplicate_flow.pipeline_definition
        duplicate_flow_pipeline_definition.update(
            dict(
                pipelineId=created_pipeline_definition.get("pipelineId"),
                uuid=created_pipeline_definition.get("uuid"),
                info=created_pipeline_definition.get("info"),
            )
        )
        duplicate_flow.pipeline_definition = duplicate_flow_pipeline_definition
        self.update_flow(duplicate_flow)

        return duplicate_flow

    @property
    def engines(self) -> list[Engine]:
        """Returns a list of Engines within project."""
        # TODO: replace with CollectionModel when implemented
        query_params = {
            "project_id": self.metadata.guid,
        }
        api_response = self._platform._engine_api.get_engines(params=query_params).json()

        return [
            Engine(platform=self._platform, project=self, **engine_json)
            for engine_json in api_response.get("streamsets_engines", [])
        ]

    def get_engine(self, asset_id: str) -> Engine:
        """Retrieve an engine by its asset_id.

        Args:
            asset_id (str): The asset_id of the engine to retrieve.

        Returns:
            Engine: The retrieved engine.

        Raises:
            HTTPError: If the request fails.
        """
        query_params = {
            "project_id": self.metadata.guid,
        }
        api_response = self._platform._engine_api.get_engine(engine_id=asset_id, params=query_params)
        return Engine(platform=self._platform, project=self, **api_response.json())

    def delete_engine(self, engine: Engine) -> requests.Response:
        """Allows to delete specified Engine within project.

        Args:
            engine: Instance of an Engine to delete.

        Returns:
            A HTTP response.
        """
        query_params = {"project_id": self.metadata.guid}
        return self._platform._engine_api.delete_engine(engine_id=engine.metadata.asset_id, params=query_params)

    @property
    def connections(self) -> Connections:
        """Retrieves connections associated with the project.

        Returns:
            A Connections object.
        """
        return Connections(platform=self._platform, project=self)

    def get_connection(self, asset_id: str) -> Connection:
        """Retrieves connection by id associated with the project.

        Args:
            asset_id: Id of the connection asset to retrieve.

        Returns:
            Retrieved Connection object.
        """
        connection_json = self._platform._connections_api.get_connection(
            id=asset_id,
            params={
                "project_id": self.metadata.guid,
            },
        ).json()

        return Connection(platform=self._platform, project=self, **connection_json)

    def create_connection(
        self,
        name: str,
        datasource_type: DatasourceType,
        description: str | None = None,
        properties: dict | None = None,
    ) -> Connection:
        """Create a Connection.

        Args:
            name: name for the new connection.
            description: description for the new connection.
            datasource_type: type of the datasource.
            properties: properties of the new connection.

        Returns:
            Created Connection object.
        """
        data = {
            "name": name,
            "datasource_type": datasource_type.metadata.asset_id,
        }
        if description:
            data["description"] = description
        if properties:
            data["properties"] = properties
        params = {
            "project_id": self.metadata.guid,
        }
        response = self._platform._connections_api.add_connection(data=json.dumps(data), params=params)
        return Connection(platform=self._platform, project=self, **response.json())

    def delete_connection(self, connection: Connection) -> requests.Response:
        """Remove the Connection.

        Returns:
            A HTTP response.
        """
        return connection._delete()

    def update_connection(self, connection: Connection) -> requests.Response:
        """Update the Connection.

        Returns:
            A HTTP response.
        """
        return connection._update()

    def copy_connection(self, connection: Connection) -> Connection:
        """Update the Connection.

        Returns:
            Copied Connection object.
        """
        return connection._copy()

    @property
    def streamsets_connections(self) -> list[StreamsetsConnection]:
        """Retrieves StreamSets connections associated with the project.

        Returns:
            A list of StreamsetsConnection within the project.
        """
        connections_json = self._platform._streamsets_flow_api.get_streamsets_connections(
            params={
                "project_id": self.metadata.guid,
            },
        ).json()

        return [
            StreamsetsConnection(
                platform=self._platform,
                project=self,
                **{
                    "entity": {
                        "datasource_type": connection["datasource_type"],
                        "name": connection["name"],
                    },
                    "metadata": {
                        "asset_id": connection["asset_id"],
                    },
                },
            )
            for connection in connections_json.get("connections", list())
        ]

    def get_streamsets_connection(
        self, id: str, version: str | None = None, type: str | None = None
    ) -> StreamsetsConnection:
        """Retrieves StreamSets connection by id associated with the project.

        Args:
            id: Id of the connection asset to retrieve.
            version: Connection version.
            type: Connection type.

        Returns:
            Retrieved StreamsetsConnection object.
        """
        params = {
            "project_id": self.metadata.guid,
        }
        if version:
            params["connection_version"] = version
        if type:
            params["connection_type"] = type

        connection_json = self._platform._streamsets_flow_api.get_streamsets_connection(
            id=id,
            params=params,
        ).json()

        # NOTE: connection_json has also 'alternative_mapping' reserved for future use
        #       this object is stripped for now as it is filled with nulls
        return StreamsetsConnection(platform=self._platform, project=self, **connection_json["connection"])


class Projects(CollectionModel):
    """Collection of Project instances."""

    def __init__(self, platform: "Platform") -> None:
        """The __init__ of the Projects class.

        Args:
            platform: The Platform object.
        """
        super().__init__(platform)
        self.unique_id = "metadata.guid"

    def __len__(self) -> int:
        """Total amount of projects."""
        return self._platform._project_api.get_projects_total().json()["total"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "bss_acount_id": None,
            "type": None,
            "member": None,
            "roles": None,
            "tag_names": None,
            "name": None,
            "match": None,
            "project_ids": None,
            "include": "name,fields,members,tags,settings",
            "limit": 100,
            "bookmark": None,
        }
        request_params_unioned = request_params_defaults
        request_params_unioned.update(request_params)
        response = self._platform._project_api.get_projects(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            response,
            Project,
            "bookmark",
            "bookmark",
            "resources",
            {"platform": self._platform},
        )

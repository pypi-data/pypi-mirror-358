#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Environment Models."""

from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from ibm_watsonx_data_integration.cpd_models import Engine
from pydantic import UUID4, Field, PrivateAttr, field_serializer, field_validator
from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import parse_qs, urlparse

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform


class EnvironmentMetadata(BaseModel):
    """The model for CPD StreamSets Environment Metadata."""

    name: str
    description: str = Field(default="")
    owner_id: str = Field(repr=False, frozen=True)
    create_time: str = Field(repr=False, frozen=True)
    project_id: UUID4 | str = Field(repr=False, frozen=True)
    asset_id: UUID4 | str = Field(repr=False, frozen=True)
    asset_attributes: list | None = Field(repr=False, frozen=True)
    asset_state: str | None = Field(repr=False, frozen=True)
    asset_type: str | None = Field(repr=False, frozen=True)
    catalog_id: UUID4 | str | None = Field(repr=False, frozen=True)
    version: float | None = Field(repr=False, frozen=True)

    _expose: bool = PrivateAttr(default=True)

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
           A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)


class EngineProperties(BaseModel):
    """The model for engine properties that are included in environments."""

    stagelibs_blocklist: list | None = Field(alias="system.stagelibs.blocklist", default=None)

    @field_validator("stagelibs_blocklist", mode="before")
    def split_string(cls, value: str | None) -> list | None:
        """Splits a stagelibs_blocklist by commas during instance creation."""
        if value is None:
            return None
        return value.split(",")

    @field_serializer("stagelibs_blocklist")
    def serialize_stagelibs(self, stagelibs: list | None) -> str | None:
        """Serializes a list of stage libraries into a comma-separated string (original format)."""
        if stagelibs is None:
            return None
        return ",".join(stagelibs)


class Environment(BaseModel):
    """The model for CPD StreamSets Environment."""

    EXPOSED_DATA_PATH = {"entity.streamsets_environment": {}}
    metadata: EnvironmentMetadata | None = Field(repr=True, default=None)
    engine_type: str | None = Field(repr=False, default=None)
    engine_version: str = Field(default=None)
    engine_properties: EngineProperties | None = Field(repr=False, default_factory=EngineProperties)
    log4j2_properties: dict | None = Field(repr=False, default_factory=dict)
    stage_libs: list | None = Field(repr=False, default_factory=list)
    jvm_options: list | None = Field(repr=False, default_factory=list)
    max_cpu_load: int | None = Field(repr=False, default=None)
    max_memory_used: int | None = Field(repr=False, default=None)
    max_flows_running: int | None = Field(repr=False, default=None)
    cpus_to_allocate: int | None = Field(repr=False, default=None)
    engine_heartbeat_interval: int | None = Field(repr=False, default=None)
    href: str | None = Field(repr=False, exclude=True, default=None)

    def __init__(self, platform: Optional["Platform"] = None, **env_json: dict) -> None:
        """The __init__ of the Environment class.

        Args:
            env_json: The JSON for the Service.
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(**env_json)
        self._platform = platform
        self._origin = self.model_dump()

    @property
    def origin(self) -> dict:
        """Returns origin model dump."""
        return self._origin

    @property
    def id(self) -> str:
        """Returns environment asset_id."""
        return self.metadata.asset_id

    @id.setter
    def id(self, value: str) -> None:
        """Set environment asset_id value. If metadata.asset_id is frozen it will raise ValidationError."""
        self.metadata.asset_id = value

    def get_installation_command(self, pretty: bool = True, foreground: bool = False) -> str | None:
        """Returns the installation command for the environment."""
        query_params = {"project_id": self.metadata.project_id, "pretty": pretty, "foreground": foreground}
        command = self._platform._environment_api.get_docker_run_command(
            env_id=self.metadata.asset_id, params=query_params
        )
        if command.status_code == 200:
            return command.text

    @property
    def engines(self) -> list[Engine]:
        """Returns list of Engines."""
        query_params = {
            "project_id": self.metadata.project_id,
        }
        response = self._platform._environment_api.get_engines(self.id, params=query_params)  # noqa
        return [Engine(platform=self._platform, **data) for data in response.json()["streamsets_engines"]]

    def add_stage_libraries(self, stage_libs: list) -> None:
        """Allows to add stage libraries to the environment.

        Args:
            stage_libs: List of stage libraries to add.
        """
        self.stage_libs.extend(stage_libs)
        self.stage_libs = sorted(set(self.stage_libs))

    def model_dump(self, *, by_alias: bool = True, exclude_unset: bool = True, **kwargs: dict) -> dict:
        """Changing default parameters of model_dump to make sure that serialized json math API response.

        Args:
            by_alias: Whether to use alias names in serialization.
            exclude_unset: Whether to exclude unset fields from serialization.
            **kwargs: Additional keyword arguments to pass to the model_dump method.

        Returns:
            A dictionary representation of the model.
        """
        return super().model_dump(exclude_unset=exclude_unset, by_alias=by_alias, **kwargs)


class Environments(CollectionModel):
    """Colelction of Environments instances."""

    def __init__(self, platform: "Platform", project: "Project") -> None:
        """The __init__ of the Environment class.

        Args:
            platform: The Platform object.
            project: The Project object.
        """
        super().__init__(platform=platform)
        self.unique_id = "metadata.asset_id"
        self._project = project

    def __len__(self) -> int:
        """Total amount of environments."""
        params = {"project_id": self._project.metadata.guid, "limit": 0}
        return self._platform._environment_api.get_environments(params=params).json().get("total_count")

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns retults of an api request."""
        request_params_defaults = {"project_id": self._project.metadata.guid, "limit": 100, "start": None, "sort": None}

        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(request_params)
        if isinstance(value := request_params_unioned.get("start"), dict):
            request_params_unioned["start"] = parse_qs(urlparse(value.get("href")).query)["start"][0]

        response = self._platform._environment_api.get_environments(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            results=response,
            class_type=Environment,
            response_bookmark="next",
            request_bookmark="start",
            response_location="streamsets_environments",
            constructor_params={"platform": self._platform},
        )

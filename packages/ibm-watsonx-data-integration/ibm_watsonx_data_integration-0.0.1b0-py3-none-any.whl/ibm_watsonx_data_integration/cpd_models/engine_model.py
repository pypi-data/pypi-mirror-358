#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing Engine Models."""

from ibm_watsonx_data_integration.common.models import BaseModel
from ibm_watsonx_data_integration.services.streamsets.api.sdc_api import DataCollectorAPIClient
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform


class EngineMetadata(BaseModel):
    """The model for CPD StreamSets Engine Metadata."""

    name: str = Field(repr=False)
    description: str = Field(repr=False)
    owner: str = Field(repr=False, default=None)
    owner_id: str = Field(repr=False)
    created: int = Field(repr=False)
    created_at: str = Field(repr=False)

    tags: list | None = Field(repr=False, default_factory=list)

    project_id: str = Field(repr=False)
    asset_id: str = Field(repr=True)
    asset_attributes: list | None = Field(repr=False)
    asset_state: str | None = Field(repr=False)
    asset_type: str | None = Field(repr=False)
    origin_country: str | None = Field(repr=False, default=None)
    catalog_id: str = Field(repr=False)
    rating: int | None = Field(repr=False)
    size: int | None = Field(repr=False)
    space_id: str = Field(repr=False, default=None)
    rov: dict | None = Field(repr=False)
    usage: dict | None = Field(repr=False)
    version: int | None = Field(repr=False)

    create_time: str | None = Field(repr=False, default=None)
    sandbox_id: str = Field(repr=False)
    creator_id: str = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class LibraryDefinitions(BaseModel):
    """An engine's library definition."""

    _expose: bool = PrivateAttr(default=False)

    schema_version: str = Field(alias="schemaVersion", repr=False)
    pipeline: list[dict] = Field(alias="pipeline", repr=False)
    pipeline_fragment: list[dict] = Field(alias="pipelineFragment", repr=False)
    pipeline_rules: list[dict] = Field(alias="pipelineRules", repr=False)
    stages: list[dict] = Field(alias="stages", repr=False)
    services: list[dict] = Field(alias="services", repr=False)
    rules_el_metadata: dict = Field(alias="rulesElMetadata", repr=False)
    el_catalog: Any = Field(alias="elCatalog", repr=False)
    runtime_configs: list[Any] = Field(alias="runtimeConfigs", repr=False)
    stage_icons: Any = Field(alias="stageIcons", repr=False)
    legacy_stage_libs: list[dict] = Field(alias="legacyStageLibs", repr=False)
    event_definitions: dict = Field(alias="eventDefinitions", repr=False)
    version: int | None = Field(alias="version", repr=False)
    executor_version: str | None = Field(alias="executorVersion", repr=False)
    category: Any | None = Field(alias="category", repr=False)
    category_label: str | None = Field(alias="categoryLabel", repr=False)
    stage_definition_map: dict | None = Field(alias="stageDefinitionMap", repr=False)
    stage_definition_minimal_list: list[dict] | None = Field(alias="stageDefinitionMinimalList", repr=False)


class Engine(BaseModel):
    """The Model for Engine."""

    EXPOSED_DATA_PATH = {
        "entity.streamsets_engine": {},
    }

    metadata: EngineMetadata = Field(repr=True)

    registration_status: str | None = Field(repr=False)
    registration_time: int = Field(repr=False)
    reported_engine_version: str = Field(repr=False, default=None)
    reported_build_time: int = Field(repr=False, default=None)
    reported_build_sha: str = Field(repr=False, default=None)
    reported_java_vendor: str | None = Field(repr=False, default=None)
    reported_java_version: str = Field(repr=False, default=None)
    reported_os_name: str = Field(repr=False, default=None)
    reported_os_arch: str = Field(repr=False, default=None)
    reported_os_version: str = Field(repr=False, default=None)
    last_startup_time: int = Field(repr=True, default=None)
    engine_type: str = Field(repr=True)
    url: str = Field(repr=True, default=None)
    streamsets_environment_asset_id: str = Field(repr=False)

    model_config = ConfigDict(frozen=True)

    def __init__(self, platform: "Platform" = None, project: "Project" = None, **engine_json: dict) -> None:
        """The __init__ of the Engine class.

        Args:
            platform: The Platform object.
            project: The Project object.
            engine_json: The JSON for the Engine.
        """
        super().__init__(**engine_json)
        self._platform = platform
        self._project = project

    def __str__(self) -> str:
        """Custom __str__ to include the product property.

        Returns:
            A string representation of class.
        """
        return f"Engine(name={self.metadata.name}, engine_id={self.metadata.asset_id}, \
            project_id={self.metadata.project_id})"

    @property
    def api_client(self) -> DataCollectorAPIClient:
        """The API Client connected directly to the engine."""
        return DataCollectorAPIClient(auth=self._platform._engine_api._auth, engine_url=self.url)

    @property
    def library_definitions(self) -> LibraryDefinitions:
        """Library Definitions of the Engine."""
        return LibraryDefinitions(**self.api_client.get_library_definitions().json())

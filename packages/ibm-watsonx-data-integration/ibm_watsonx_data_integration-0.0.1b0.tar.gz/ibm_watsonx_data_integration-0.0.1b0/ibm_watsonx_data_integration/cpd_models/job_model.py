#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025


"""Module containing Job and Job Run Models."""

import json
import requests
from enum import Enum
from ibm_watsonx_data_integration.common.models import BaseModel, CollectionModel, CollectionModelResults
from pydantic import ConfigDict, Field, PrivateAttr
from typing import TYPE_CHECKING, Any, ClassVar, Optional
from typing_extensions import override

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.cpd_models import Project
    from ibm_watsonx_data_integration.platform import Platform


class Outputs(BaseModel):
    """Holds job configuration output information."""

    total_rows_read: int = Field(repr=False, default=0)
    total_rows_written: int = Field(repr=False, default=0)
    total_bytes_read: int = Field(repr=False, default=0)
    total_bytes_written: int = Field(repr=False, default=0)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class JobConfiguration(BaseModel):
    """Holds configuration parameters which Job was run."""

    env_id: str = Field(repr=False, default="")
    env_type: str = Field(repr=False, default="")
    env_variables: list[str] | None = Field(repr=False, default_factory=list)
    version: str = Field(repr=False, default="")
    deployment_job_definition_id: str = Field(repr=False, default="")
    outputs: Outputs = Field(frozen=True, repr=False, default_factory=Outputs)

    _expose: bool = PrivateAttr(default=False)


class JobParameter(BaseModel):
    """Parameter used when running job.

    Represents parameter used by Connectors and Stages to dynamically
    change value.
    """

    name: str
    value: Any

    _expose: bool = PrivateAttr(default=False)


class ParameterSet(BaseModel):
    """Parameter sets."""

    name: str
    value_set: str
    ref: str = Field(frozen=True, repr=False)

    _expose: bool = PrivateAttr(default=False)


class RetentionPolicy(BaseModel):
    """Retention policy model."""

    days: int | None = None
    amount: int | None = None

    _expose: bool = PrivateAttr(default=False)


class ScheduleInfo(BaseModel):
    """Represent schedule configuration for Job."""

    repeat: bool | None = None
    start_on: int | None = Field(alias="startOn", default=None)
    end_on: int | None = Field(alias="endOn", default=None)

    # TODO: change to `validate_by_name` when update pydantic version >=2.11
    model_config = ConfigDict(populate_by_name=True)
    _expose: bool = PrivateAttr(default=False)


class JobRunState(Enum):
    """Available states for Job Run."""

    Queued = "Queued"
    Starting = "Starting"
    Running = "Running"
    Paused = "Paused"
    Resuming = "Resuming"
    Canceling = "Canceling"
    Canceled = "Canceled"
    Failed = "Failed"
    Completed = "Completed"
    CompletedWithErrors = "CompletedWithErrors"
    CompletedWithWarnings = "CompletedWithWarnings"


class JobRunMetadata(BaseModel):
    """Model representing metadata for a Job Run."""

    name: str = Field(repr=True)
    asset_id: str = Field(repr=False)
    owner_id: str = Field(repr=False)
    created: int = Field(repr=False)
    created_at: str = Field(repr=False)
    usage: dict[str, Any] = Field(repr=False)

    model_config = ConfigDict(frozen=True)
    _expose: bool = PrivateAttr(default=False)


class JobRun(BaseModel):
    """The model for CPD Job Run."""

    metadata: JobRunMetadata = Field(repr=True)

    job_ref: str = Field(repr=False)
    job_name: str = Field(repr=True)
    job_type: str = Field(repr=False)
    state: str = Field(repr=True)
    is_scheduled_run: bool = Field(alias="isScheduledRun", repr=False, default=False)
    configuration: JobConfiguration = Field(repr=False)
    project_name: str | None = Field(repr=False, default=None)
    queue_start: int | None = Field(repr=False, default=None)
    last_state_change_timestamp: str | None = Field(repr=False, default=None)
    job_parameters: list[JobParameter] | None = Field(repr=False, default=None)
    queue_end: int | None = Field(repr=False, default=None)
    runtime_job_id: str | None = Field(repr=False, default=None)
    parameter_sets: list[ParameterSet] | None = Field(repr=False, default=None)
    execution_start: int | None = Field(repr=False, default=None)
    resource_usage: float | None = Field(repr=False, default=None)
    total_stages: int | None = Field(repr=False, default=None)
    total_rows_written: int | None = Field(repr=False, default=None)
    execution_end: int | None = Field(repr=False, default=None)
    duration: int | None = Field(repr=False, default=None)
    total_rows_read: int | None = Field(repr=False, default=None)

    model_config = ConfigDict(frozen=True)
    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity.job_run": {}}

    def __init__(
        self, platform: Optional["Platform"] = None, project: Optional["Project"] = None, **job_run_json: dict
    ) -> None:
        """The __init__ of the Job Run class.

        Args:
            platform: The Platform object.
            project: The Project object.
            job_run_json: The JSON for the Job Run.
        """
        super().__init__(**job_run_json)
        self._platform = platform
        self._project = project

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

    def cancel(self) -> requests.Response:
        """Stop already started Job Run.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
        """
        query_params = {
            "project_id": self._project.metadata.guid,
        }
        return self._platform._job_api.cancel_job_run(  # noqa
            run_id=self.metadata.asset_id, job_id=self.job_ref, data=None, params=query_params
        )

    @property
    def logs(self) -> list[str]:
        """Retrieves runtime logs for a job run.

        Returns:
            A list containing runtime log entries that describe the job run execution.
            Each entry is a single log line from the UI.
        """
        query_params = {
            "project_id": self._project.metadata.guid,  # noqa
        }
        res = self._platform._job_api.get_job_run_logs(  # noqa
            run_id=self.metadata.asset_id, job_id=self.job_ref, params=query_params
        )
        logs_json = res.json()
        return logs_json.get("results", list())


class JobRuns(CollectionModel):
    """Collection of Job Run instances."""

    def __init__(self, platform: "Platform", project: "Project", job_id: str) -> None:
        """The __init__ of the JobRuns class.

        Args:
            platform: The Platform object.
            project: Instance of Project in which job run was created.
            job_id: ID of Job for which runs was stared.
        """
        super().__init__(platform)
        self.unique_id = "metadata.asset_id"
        self._project = project
        self._job_id = job_id

    @override
    def __len__(self) -> int:
        query_params = {
            "project_id": self._project.metadata.guid,
            "limit": 1,  # Use lowest `limit` since we need only `total_rows`
        }
        res = self._platform._job_api.get_job_runs(params=query_params, job_id=self._job_id)
        res_json = res.json()
        return res_json["total_rows"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": self._project.metadata.guid,
            "space_id": None,
            "states": None,
            "limit": 100,
            "next": None,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(request_params)

        if isinstance(request_params_unioned.get("states"), list):
            request_params_unioned["states"] = ",".join(request_params_unioned.get("states"))

        # Based on APISpec, query param `next` expect JSON string of `next` from previous call
        if isinstance(request_params_unioned.get("next"), dict):
            request_params_unioned["next"] = json.dumps(request_params_unioned["next"])

        response = self._platform._job_api.get_job_runs(
            params={k: v for k, v in request_params_unioned.items() if v is not None}, job_id=self._job_id
        ).json()
        return CollectionModelResults(
            response,
            JobRun,
            "next",
            "next",
            "results",
            {"platform": self._platform, "project": self._project},
        )


class JobMetadata(BaseModel):
    """Model representing metadata for a job."""

    name: str = Field(repr=True)
    description: str | None = Field(repr=False, default="")
    asset_id: str = Field(frozen=True, repr=False)
    owner_id: str = Field(frozen=True, repr=False)
    version: int = Field(repr=True)

    _expose: bool = PrivateAttr(default=False)


class Job(BaseModel):
    """The model for CPD Job."""

    metadata: JobMetadata = Field(repr=True)

    asset_ref: str = Field(frozen=True, repr=False)
    asset_ref_type: str = Field(frozen=True, repr=False)
    configuration: JobConfiguration = Field(repr=False)
    last_run_status_timestamp: int = Field(frozen=True, repr=False)
    future_scheduled_runs: list = Field(repr=False)
    enable_notifications: bool = Field(repr=False)
    project_name: str = Field(frozen=True, repr=True)
    schedule: str | None = Field(repr=False, default=None)
    schedule_info: ScheduleInfo | None = Field(repr=False, default=None)
    schedule_id: str = Field(frozen=True, repr=False)
    schedule_creator_id: str = Field(frozen=True, repr=False)
    job_parameters: list[JobParameter] | None = Field(default=None, repr=False)
    parameter_sets: list[ParameterSet] | None = Field(default=None, repr=False)

    EXPOSED_DATA_PATH: ClassVar[dict] = {"entity.job": {}}

    def __init__(
        self, platform: Optional["Platform"] = None, project: Optional["Project"] = None, **job_json: dict
    ) -> None:
        """The __init__ of the Job class.

        Args:
            platform: The Platform object.
            project: The Project object.
            job_json: The JSON for the Job.
        """
        super().__init__(**job_json)
        self._platform = platform
        self._project = project
        self._origin = self.model_dump()

    @property
    def origin(self) -> dict:
        """Returns origin model dump."""
        return self._origin

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

    @property
    def job_runs(self) -> JobRuns:
        """Returns a list of Job Runs of the job.

        Returns:
            A list of jobs runs for the given job.
        """
        return JobRuns(platform=self._platform, project=self._project, job_id=self.metadata.asset_id)

    def delete_job_run(self, job_run: JobRun) -> requests.Response:
        """Delete given run of job.

        Args:
            job_run: Instance of a Job Run to delete.

        Returns:
            A HTTP response. If it is 204, then the operation completed successfully.
            If the code is 202, then the operation is in progress.
        """
        query_params = {
            "project_id": self._project.metadata.guid,  # noqa
        }
        return self._platform._job_api.delete_job_run(  # noqa
            run_id=job_run.metadata.asset_id, job_id=self.metadata.asset_id, params=query_params
        )

    def start(
        self,
        name: str,
        description: str,
        configuration: dict[str, Any] | None = None,
        job_parameters: dict[str, Any] | None = None,
        parameter_sets: list[dict[str, str]] | None = None,
    ) -> JobRun:
        """Create Job Run for given configuration.

        Args:
            name: Name for a Job Run.
            description: Description for a Job Run.
            configuration: Environment variables.
            job_parameters: Parameters use internally by a Job.
            parameter_sets: Parameter sets for a Job Run.

        Returns:
            An instance of a Job Run.
        """
        query_params = {
            "project_id": self._project.metadata.guid,  # noqa
        }

        new_data = {
            "name": name,
            "description": description,
        }

        if configuration:
            new_data["configuration"] = configuration

        if job_parameters:
            new_data["job_parameters"] = [{"name": k, "value": v} for k, v in job_parameters.items()]

        if parameter_sets:
            new_data["parameter_sets"] = parameter_sets

        data = {"job_run": new_data}
        res = self._platform._job_api.create_job_run(  # noqa
            job_id=self.metadata.asset_id, data=json.dumps(data), params=query_params
        )
        job_run_json = res.json()
        return JobRun(platform=self._platform, project=self._project, **job_run_json)


class Jobs(CollectionModel):
    """Collection of Job instances."""

    def __init__(self, platform: "Platform", project: "Project") -> None:
        """The __init__ of the Jobs class.

        Args:
            platform: The Platform object.
            project: Instance of Project in which job was created.
        """
        super().__init__(platform)
        self.unique_id = "metadata.asset_id"
        self._project = project

    @override
    def __len__(self) -> int:
        query_params = {
            "project_id": self._project.metadata.guid,
            "limit": 1,  # Use lowest `limit` since we need only `total_rows`
        }
        res = self._platform._job_api.get_jobs(params=query_params)
        res_json = res.json()
        return res_json["total_rows"]

    def _get_results_from_api(self, request_params: dict = None, **kwargs: dict) -> CollectionModelResults:
        """Returns results of an api request."""
        request_params_defaults = {
            "project_id": self._project.metadata.guid,
            "space_id": None,
            "asset_ref": None,
            "asset_ref_type": None,
            "run_id": None,
            "limit": 100,
            "next": None,
        }
        request_params_unioned: dict[str, Any] = request_params_defaults
        request_params_unioned.update(request_params)

        # Based on APISpec, query param `next` expect JSON string of `next` from previous call
        if isinstance(request_params_unioned.get("next"), dict):
            request_params_unioned["next"] = json.dumps(request_params_unioned["next"])

        response = self._platform._job_api.get_jobs(
            params={k: v for k, v in request_params_unioned.items() if v is not None}
        ).json()
        return CollectionModelResults(
            response,
            Job,
            "next",
            "next",
            "results",
            {"platform": self._platform, "project": self._project},
        )

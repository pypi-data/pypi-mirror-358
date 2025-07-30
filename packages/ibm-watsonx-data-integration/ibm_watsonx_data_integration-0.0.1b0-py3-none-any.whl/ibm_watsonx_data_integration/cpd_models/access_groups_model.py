#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2025

"""Module containing AccessGroup Model."""

from ibm_watsonx_data_integration.common.models import BaseModel
from pydantic import Field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ibm_watsonx_data_integration.platform import Platform


class AccessGroup(BaseModel):
    """Model representing an Access Group, including Rules."""

    id: str = Field(frozen=True, repr=False)
    name: str = Field(repr=True)
    description: str = Field(repr=True)
    account_id: str = Field(repr=False, frozen=True)
    created_at: str = Field(repr=False, frozen=True)
    created_by_id: str = Field(repr=False, frozen=True)
    last_modified_at: str = Field(repr=False, frozen=True)
    last_modified_by_id: str = Field(repr=False, frozen=True)

    def __init__(self, platform: Optional["Platform"] = None, **access_group_json: dict) -> None:
        """The __init__ of the AccessGroup class.

        Args:
            platform: The Platform object.
            access_group_json: The JSON for the AccessGroup.
        """
        super().__init__(**access_group_json)
        self._platform = platform

from typing import Optional

from pydantic import ConfigDict, Field

from pa_api.xmlapi.types.utils import (
    Bool,
    Datetime,
    String,
    XMLBaseModel,
)


class SoftwareVersion(XMLBaseModel):
    model_config = ConfigDict(extra="ignore")

    version: String
    filename: String
    released_on: Optional[Datetime] = Field(alias="released-on")
    downloaded: Bool
    current: Bool
    latest: Bool
    uploaded: Bool

    @property
    def base_minor_version(self) -> str:
        major, minor, _ = self.version.split(".")
        return f"{major}.{minor}.0"

    @property
    def base_major_version(self) -> str:
        major, _, _ = self.version.split(".")
        return f"{major}.0.0"

from pydantic import ConfigDict, Field

from pa_api.xmlapi.types.utils import (
    String,
    XMLBaseModel,
)


class SystemInfo(XMLBaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    hostname: String
    ip_address: String = Field(alias="ip-address")
    netmask: String
    mac_address: String = Field(alias="mac-address")
    devicename: String
    serial: String
    model: String
    sw_version: String = Field(alias="sw-version")

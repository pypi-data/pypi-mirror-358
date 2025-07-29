from typing import Optional

from pydantic import AliasPath, ConfigDict, Field

from pa_api.xmlapi.types.utils import List, String, XMLBaseModel


class ZoneNetwork(XMLBaseModel):
    model_config = ConfigDict(extra="allow")

    name: String = Field(validation_alias="@name", default="")
    layer3: List[String] = Field(
        validation_alias=AliasPath("layer3", "member"),
        default_factory=list,
    )
    enable_packet_buffer_protection: Optional[bool] = Field(
        validation_alias=AliasPath("enable-packet-buffer-protection", "#text"),
        default=None,
    )


class Zone(XMLBaseModel):
    model_config = ConfigDict(extra="allow")

    name: String = Field(validation_alias="@name", default="")
    network: Optional[ZoneNetwork] = None
    enable_user_identification: Optional[bool] = Field(
        validation_alias=AliasPath("enable-user-identification", "#text"), default=None
    )
    enable_device_identification: Optional[bool] = Field(
        validation_alias=AliasPath("enable-device-identification", "#text"),
        default=None,
    )

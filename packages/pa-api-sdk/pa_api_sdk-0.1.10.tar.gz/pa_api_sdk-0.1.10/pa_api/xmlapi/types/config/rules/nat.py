import typing
from itertools import chain
from typing import Optional, Union

from pydantic import AliasPath, Field

from pa_api.xmlapi.types.utils import List, String, XMLBaseModel


class DynamicIPAndPort(XMLBaseModel):
    translated_address: List[String] = Field(
        validation_alias="translated-address", default=None
    )
    ip: Optional[String] = Field(
        validation_alias=AliasPath("interface-address", "ip"), default=None
    )
    interface: Optional[String] = Field(
        validation_alias=AliasPath("interface-address", "interface"), default=None
    )


class DynamicIP(XMLBaseModel):
    translated_address: List[String] = Field(
        validation_alias="translated-address", default=None
    )


class StaticIP(XMLBaseModel):
    translated_address: String = Field(validation_alias="translated-address")


class SourceTranslation(XMLBaseModel):
    dynamic_ip_and_port: Optional[DynamicIPAndPort] = Field(
        validation_alias="dynamic-ip-and-port", default=None
    )
    dynamic_ip: Optional[DynamicIP] = Field(validation_alias="dynamic-ip", default=None)
    static_ip: Optional[StaticIP] = Field(validation_alias="static-ip", default=None)

    @property
    def translation(self) -> Union[DynamicIPAndPort, DynamicIP, StaticIP]:
        for trans in (self.dynamic_ip_and_port, self.dynamic_ip, self.static_ip):
            if trans is not None:
                return trans
        raise Exception("Invalid sourc translation")

    @property
    def translated_address(self) -> typing.List[str]:
        trans = self.translation.translated_address
        if isinstance(trans, str):
            return [trans]
        return trans

    @property
    def type(self) -> str:
        if self.static_ip is not None:
            return "static-ip"
        if self.dynamic_ip is not None:
            return "dynamic-ip"
        if self.dynamic_ip_and_port is not None:
            return "dynamic-ip-and-port"
        raise Exception("Invalid sourc translation")


class DestinationTranslation(XMLBaseModel):
    translated_address: Optional[String] = Field(
        validation_alias=AliasPath("translated-address", "#text"), default=None
    )
    translated_port: Optional[int] = Field(
        validation_alias=AliasPath("translated-port", "#text"), default=None
    )


class NAT(XMLBaseModel):
    name: String = Field(validation_alias="@name")
    uuid: String = Field(validation_alias="@uuid")
    disabled: Optional[bool] = None
    description: String = ""
    group_tag: Optional[String] = Field(validation_alias="group-tag", default=None)
    tags: List[String] = Field(
        validation_alias="tag",
        default_factory=list,
    )
    services: List[String] = Field(validation_alias="service", default_factory=list)

    source_translation: Optional[SourceTranslation] = Field(
        validation_alias="source-translation", default=None
    )
    destination_translation: Optional[DestinationTranslation] = Field(
        validation_alias="destination-translation", default=None
    )

    sources: List[String] = Field(
        validation_alias="source",
        default_factory=list,
    )
    destinations: List[String] = Field(
        validation_alias="destination",
        default_factory=list,
    )
    to: List[String] = Field(
        validation_alias="to",
        default_factory=list,
    )
    from_: List[String] = Field(
        validation_alias="from",
        default_factory=list,
    )

    @property
    def translated_src_address(self) -> typing.List[str]:
        if not self.source_translation:
            return []
        return self.source_translation.translated_address

    @property
    def translated_dst_address(self) -> typing.List[str]:
        if not self.destination_translation:
            return []
        translated = self.destination_translation.translated_address
        if not translated:
            return []
        return [translated]

    @property
    def members(self):
        return set(
            chain(
                self.to,
                self.from_,
                self.sources,
                self.destination_translation,
                self.translated_src_address,
                self.translated_dst_address,
            )
        )

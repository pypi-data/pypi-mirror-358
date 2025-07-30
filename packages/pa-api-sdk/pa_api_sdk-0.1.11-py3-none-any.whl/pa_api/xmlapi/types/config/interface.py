from ipaddress import ip_network
from typing import ClassVar, Iterable, Optional

from pydantic import AliasPath, ConfigDict, Field

from pa_api.xmlapi.types.utils import Ip, List, String, XMLBaseModel


def get_ip_network(ip_netmask):
    try:
        if ip_netmask:
            return ip_network(ip_netmask, strict=False)
    except Exception:
        return None


class GenericInterface(XMLBaseModel):
    model_config = ConfigDict(extra="ignore")
    inttype: str
    parent: Optional[str] = None
    name: str
    description: String = ""
    comment: String = ""
    ip: List[str] = Field(default_factory=list)
    untagged_sub_interface: Optional[String] = None
    tags: List[String] = Field(default_factory=list)
    link_state: Optional[str] = None
    link_speed: Optional[str] = None
    link_duplex: Optional[str] = None
    aggregate_group: Optional[String] = None


class Layer2(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "layer2"

    name: String = Field(validation_alias="@name", default="")
    units: List["Layer2"] = Field(
        alias="units",
        validation_alias=AliasPath("units", "entry"),
        default_factory=list,
    )
    comment: String = ""
    tags: List[String] = Field(
        validation_alias=AliasPath("tag", "member"),
        default_factory=list,
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        if self.name:
            dump = self.model_dump()
            dump.update(
                {
                    "inttype": self.inttype,
                    "parent": parent,
                }
            )
            generic = GenericInterface.model_validate(dump)
            yield generic
            parent = self.name
        for u in self.units:
            yield from u.flatten(parent)


class Layer3(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "layer3"

    name: Optional[String] = Field(validation_alias="@name", default=None)
    description: String = Field(validation_alias="#text", default="")
    ip: List[Ip] = Field(
        validation_alias=AliasPath("ip", "entry"), default_factory=list
    )
    untagged_sub_interface: Optional[String] = Field(
        alias="untagged-sub-interface",
        default=None,
    )
    units: List["Layer3"] = Field(
        alias="units",
        validation_alias=AliasPath("units", "entry"),
        default_factory=list,
    )
    comment: String = ""
    tags: List[String] = Field(
        validation_alias=AliasPath("tag", "member"),
        default_factory=list,
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        if self.name:
            dump = self.model_dump()
            dump.update(
                {
                    "inttype": self.inttype,
                    "parent": parent,
                }
            )
            generic = GenericInterface.model_validate(dump)
            yield generic
            parent = self.name
        for u in self.units:
            yield from u.flatten(parent)


class Vlan(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "vlan"

    name: Optional[String] = Field(validation_alias="@name", default=None)
    description: String = Field(validation_alias="#text", default="")
    ip: List[Ip] = Field(
        validation_alias=AliasPath("ip", "entry"), default_factory=list
    )
    # untagged_sub_interface: Optional[String] = Field(
    #     alias="untagged-sub-interface",
    #     default=None,
    # )
    units: List["Vlan"] = Field(
        alias="units",
        validation_alias=AliasPath("units", "entry"),
        default_factory=list,
    )
    comment: String = ""
    tags: List[String] = Field(
        validation_alias=AliasPath("tag", "member"),
        default_factory=list,
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        if self.name:
            dump = self.model_dump()
            dump.update(
                {
                    "inttype": self.inttype,
                    "parent": parent,
                }
            )
            generic = GenericInterface.model_validate(dump)
            yield generic
            parent = self.name
        for u in self.units:
            yield from u.flatten(parent)


class Ethernet(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "ethernet"

    name: str = Field(validation_alias="@name")
    ip: List[str] = Field(
        validation_alias=AliasPath("layer3", "ip", "entry", "@name"),
        default_factory=list,
    )
    description: String = Field(validation_alias="#text", default="")
    link_state: Optional[str] = Field(
        alias="link-state",
        validation_alias=AliasPath("link-state", "#text"),
        default=None,
    )
    link_speed: Optional[str] = Field(
        alias="link-speed",
        validation_alias=AliasPath("link-speed", "#text"),
        default=None,
    )
    link_duplex: Optional[str] = Field(
        alias="link-duplex",
        validation_alias=AliasPath("link-duplex", "#text"),
        default=None,
    )
    aggregate_group: Optional[String] = Field(
        alias="aggregate-group",
        default=None,
    )
    layer2: Optional[Layer2] = Field(alias="layer2", default=None)
    layer3: Optional[Layer3] = Field(alias="layer3", default=None)
    tags: List[String] = Field(
        validation_alias=AliasPath("tag", "member"),
        default_factory=list,
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        if self.name:
            dump = self.model_dump()
            dump.update(
                {
                    "inttype": self.inttype,
                    "parent": parent,
                }
            )
            generic = GenericInterface.model_validate(dump)
            yield generic
            parent = self.name
        if self.layer2:
            yield from self.layer2.flatten(parent)
        if self.layer3:
            yield from self.layer3.flatten(parent)


class AggregateEthernet(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "aggregate"

    name: str = Field(validation_alias="@name")
    ip: List[str] = Field(
        validation_alias=AliasPath("layer3", "ip", "entry", "@name"),
        default_factory=list,
    )
    description: String = Field(validation_alias="#text", default="")
    comment: String = ""
    units: List["AggregateEthernet"] = Field(
        alias="units",
        validation_alias=AliasPath("units", "entry"),
        default_factory=list,
    )
    layer2: Optional[Layer2] = Field(alias="layer2", default=None)
    layer3: Optional[Layer3] = Field(alias="layer3", default=None)
    untagged_sub_interface: Optional[String] = Field(
        alias="untagged-sub-interface",
        default=None,
    )
    tags: List[String] = Field(
        validation_alias=AliasPath("tag", "member"),
        default_factory=list,
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        if self.name:
            dump = self.model_dump()
            dump.update(
                {
                    "inttype": self.inttype,
                    "parent": parent,
                }
            )
            generic = GenericInterface.model_validate(dump)
            yield generic
            parent = self.name
        if self.layer2:
            yield from self.layer2.flatten(parent)
        if self.layer3:
            yield from self.layer3.flatten(parent)


class Tunnel(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "tunnel"

    name: str = Field(validation_alias="@name")
    units: List["Tunnel"] = Field(
        alias="units",
        validation_alias=AliasPath("units", "entry"),
        default_factory=list,
    )
    ip: List[str] = Field(
        validation_alias=AliasPath("ip", "entry", "@name"),
        default_factory=list,
    )
    interface_management_profile: Optional[String] = Field(
        validation_alias="interface-management-profile", default=None
    )

    comment: Optional[str] = Field(
        alias="comment", validation_alias=AliasPath("comment", "#text"), default=None
    )
    mtu: Optional[str] = Field(
        alias="comment", validation_alias=AliasPath("mtu", "#text"), default=None
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        dump = self.model_dump()
        dump.update(
            {
                "inttype": self.inttype,
                "parent": parent,
            }
        )
        generic = GenericInterface.model_validate(dump)
        yield generic


class Loopback(XMLBaseModel):
    model_config = ConfigDict(extra="allow")
    inttype: ClassVar[str] = "loopback"

    name: str = Field(validation_alias="@name")
    description: Optional[String] = Field(validation_alias="#text", default=None)
    ip: List[Ip] = Field(
        validation_alias=AliasPath("ip", "entry"), default_factory=list
    )
    comment: Optional[str] = Field(
        alias="comment", validation_alias=AliasPath("comment", "#text"), default=None
    )
    tags: List[String] = Field(
        validation_alias=AliasPath("tag", "member"),
        default_factory=list,
    )

    def flatten(self, parent=None) -> Iterable[GenericInterface]:
        dump = self.model_dump()
        dump.update(
            {
                "inttype": self.inttype,
                "parent": parent,
            }
        )
        generic = GenericInterface.model_validate(dump)
        yield generic


# https://docs.pydantic.dev/latest/concepts/alias/#aliaspath-and-aliaschoices
class Interface(XMLBaseModel):
    model_config = ConfigDict(extra="allow")

    aggregate_ethernet: List[AggregateEthernet] = Field(
        alias="aggregate-ethernet",
        validation_alias=AliasPath("aggregate-ethernet", "entry"),
        default_factory=list,
    )
    # entry = Field(alias="entry")
    ethernet: List[Ethernet] = Field(
        alias="ethernet",
        validation_alias=AliasPath("ethernet", "entry"),
        default_factory=list,
    )
    loopback: List[Loopback] = Field(
        alias="loopback",
        validation_alias=AliasPath("loopback", "units", "entry"),
        default_factory=list,
    )
    vlan: List[Vlan] = Field(
        alias="vlan",
        validation_alias=AliasPath("vlan", "units", "entry"),
        default_factory=list,
    )
    tunnel: List[Tunnel] = Field(
        alias="tunnel",
        validation_alias=AliasPath("tunnel", "units", "entry"),
        default_factory=list,
    )

    # ha1 = Field(alias='ha1')
    # ha1_backup = Field(alias='ha1-backup')
    # ha2 = Field(alias='ha2')
    # ha2_backup = Field(alias='ha2-backup')
    # ha3 = Field(alias='ha3')
    # member = Field(alias='member')
    # tunnel = Field(alias='tunnel')

    def _flatten(self) -> Iterable[GenericInterface]:
        for eth in self.ethernet:
            yield from eth.flatten()
        for agg in self.aggregate_ethernet:
            yield from agg.flatten()
        for v in self.vlan:
            yield from v.flatten()
        for lb in self.loopback:
            yield from lb.flatten()

    def flatten(self) -> List[GenericInterface]:
        return list(self._flatten())

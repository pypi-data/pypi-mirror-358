from ipaddress import IPv4Network, IPv6Network
from typing import List, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

IPNetwork = Union[IPv4Network, IPv6Network]


class Address(BaseModel):
    model_config = ConfigDict(extra="allow")

    device_group: str
    name: str = Field(validation_alias=AliasChoices("@name", "name"))
    prefix: str
    ip_netmask: str
    ip_network: IPNetwork
    ip_range: str
    fqdn: str
    tags: List[str]

    # name: str = Field(validation_alias=AliasChoices("@name", "name"))
    # device_group: str = Field(alias="device-group")
    # rulebase: Literal["pre-rulebase", "post-rulebase"] = Field(alias="rulebase")
    # ttype: str = Field(alias="type")
    # state: Optional[str] = Field(alias="rule-state")
    # modification: datetime = Field(alias="rule-modification-timestamp")
    # creation: datetime = Field(alias="rule-creation-timestamp")
    # all_connected: bool = Field(alias="all-connected")

    # @field_validator("modification", "creation", mode="before")
    # @classmethod
    # def ensure_datetime(cls, v: Any):
    #     if not isinstance(v, int):
    #         v = int(v)
    #     return datetime.fromtimestamp(v)

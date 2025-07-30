from datetime import datetime
from typing import Any, List, Literal, Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from pa_api.xmlapi.utils import el2dict as xml2dict


class RuleHit(BaseModel):
    name: str = Field(validation_alias=AliasChoices("@name", "name"))
    device_group: str = Field(alias="device-group")
    rulebase: Literal["pre-rulebase", "post-rulebase"] = Field(alias="rulebase")
    type: str = Field(alias="type")
    state: Optional[str] = Field(alias="rule-state")
    modification: datetime = Field(alias="rule-modification-timestamp")
    creation: datetime = Field(alias="rule-creation-timestamp")
    all_connected: bool = Field(alias="all-connected")

    @field_validator("modification", "creation", mode="before")
    @classmethod
    def ensure_datetime(cls, v: Any):
        if not isinstance(v, int):
            v = int(v)
        return datetime.fromtimestamp(v)

    @staticmethod
    def from_tuple(t):
        device_group, rulebase, rule_type, xml = t
        return RuleHit.model_validate(
            {
                "device-group": device_group,
                "rulebase": rulebase,
                "type": rule_type,
                **xml2dict(xml)["entry"],
            }
        )


class RuleUse(BaseModel):
    model_config = ConfigDict(extra="allow")
    name: str = Field(validation_alias=AliasChoices("@name", "name"))
    description: Optional[str] = Field(default=None)
    uuid: str = Field(validation_alias=AliasChoices("@uuid", "uuid"))
    state: Optional[str] = Field(alias="rule-state")
    bytes: Optional[int] = Field(default=None)
    group_tag: Optional[str] = Field(alias="group-tag", default=None)
    tag: Optional[List[str]] = Field(default=None)
    disabled: Optional[bool] = Field(default=None)
    rule_type: Optional[Literal["interzone", "universal"]] = Field(
        alias="rule-type", default=None
    )
    nat_type: Optional[Literal["ipv4", "ipv6"]] = Field(alias="nat-type", default=None)
    modification: datetime = Field(alias="rule-modification-timestamp")
    creation: datetime = Field(alias="rule-creation-timestamp")

    action: Optional[Union[Literal["allow", "deny", "reset-client"], dict]] = Field(
        default=None
    )
    to_interface: str = Field(alias="to-interface", default=None)
    protocol: Optional[Literal["tcp", "udp"]] = Field(default=None)
    port: Optional[str] = Field(default=None)  # Can be a port range

    to_: Optional[List[str]] = Field(alias="from", default=None)
    from_: Optional[List[str]] = Field(alias="to", default=None)
    source: Optional[List[str]] = Field(default=None)
    destination: Optional[List[str]] = Field(default=None)
    source_translation: Optional[List[str]] = Field(
        alias="source-translation", default=None
    )
    destination_translation: Optional[List[str]] = Field(
        alias="destination-translation", default=None
    )

    source_user: Optional[List[str]] = Field(alias="source-user", default=None)
    application: Optional[List[str]] = Field(default=None)
    category: Optional[List[str]] = Field(default=None)
    service: Optional[List[str]] = Field(default=None)

    icmp_unreachable: Optional[bool] = Field(alias="icmp-unreachable", default=None)
    log_start: Optional[bool] = Field(alias="log-start", default=None)
    log_end: Optional[bool] = Field(alias="log-end", default=None)
    negate_source: Optional[bool] = Field(alias="negate-source", default=None)
    negate_destination: Optional[bool] = Field(alias="negate-destination", default=None)

    @field_validator(
        "tag",
        "to_",
        "from_",
        "source",
        "destination",
        "source_translation",
        "destination_translation",
        "source_user",
        "application",
        "category",
        "service",
        mode="before",
    )
    @classmethod
    def ensure_membership(cls, v: Any):
        if v is None:
            return None
        members = v.get("member") if isinstance(v, dict) else v
        if isinstance(members, str):
            members = [members]
        return members

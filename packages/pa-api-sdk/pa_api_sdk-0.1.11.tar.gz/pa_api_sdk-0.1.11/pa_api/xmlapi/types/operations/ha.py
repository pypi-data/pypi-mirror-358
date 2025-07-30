from typing import Any, Optional

from pydantic import ConfigDict, Field, model_validator

from pa_api.xmlapi.types.utils import String, XMLBaseModel


class HALocalInfo(XMLBaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    priority: int
    preemptive: bool
    state: str
    mode: String
    ha1_backup_macaddr: str = Field(alias="ha1-backup-macaddr")
    ha1_macaddr: str = Field(alias="ha1-macaddr")
    mgmt_ip: str = Field(alias="mgmt-ip")


class HAPeerInfo(XMLBaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")
    priority: int
    preemptive: bool
    state: str
    mode: str
    conn_status: str = Field(alias="conn-status")
    ha1_backup_macaddr: str = Field(alias="ha1-backup-macaddr")
    ha1_macaddr: str = Field(alias="ha1-macaddr")
    mgmt_ip: str = Field(alias="mgmt-ip")


class HAGroup(XMLBaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    local_info: HALocalInfo = Field(alias="local-info")
    peer_info: HAPeerInfo = Field(alias="peer-info")

    @property
    def is_primary(self):
        return self.local_info.priority < self.peer_info.priority


class HAInfo(XMLBaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    enabled: bool
    group: Optional[HAGroup] = None

    @model_validator(mode="before")
    @classmethod
    def ensure_group_none_if_disabled(cls, data: dict) -> Any:
        if isinstance(data, dict):
            enabled = data.get("enabled")
            if not enabled or enabled != "yes":
                return {"enabled": "no"}
        return data

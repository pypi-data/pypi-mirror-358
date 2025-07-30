from typing import Optional

from pydantic import AliasPath, ConfigDict, Field

from pa_api.xmlapi.types.utils import List, String, XMLBaseModel


class NextHop(XMLBaseModel):
    model_config = ConfigDict(extra="ignore")

    ip_address: Optional[String] = Field(validation_alias="ip-address", default=None)


class StaticRoute(XMLBaseModel):
    model_config = ConfigDict(extra="ignore")

    name: String = Field(validation_alias="@name")
    nexthop: Optional[NextHop] = Field(validation_alias="nexthop", default=None)
    interface: Optional[String] = Field(validation_alias="interface", default=None)
    destination: String = Field(validation_alias="destination")


class IPv4RoutingTable(XMLBaseModel):
    model_config = ConfigDict(extra="ignore")

    static_routes: List[StaticRoute] = Field(
        validation_alias=AliasPath("static-route", "entry")
    )


class RoutingTable(XMLBaseModel):
    model_config = ConfigDict(extra="ignore")

    ip: IPv4RoutingTable = Field(validation_alias="ip")

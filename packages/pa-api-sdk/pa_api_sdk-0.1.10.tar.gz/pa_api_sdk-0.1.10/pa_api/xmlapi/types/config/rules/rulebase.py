from pydantic import AliasPath, ConfigDict, Field

from pa_api.xmlapi.types.utils import List, XMLBaseModel

from .nat import NAT
from .security import Security


class RuleBase(XMLBaseModel):
    model_config = ConfigDict(extra="allow")

    security: List[Security] = Field(
        validation_alias=AliasPath("security", "rules", "entry"),
        default_factory=list,
    )
    nat: List[NAT] = Field(
        validation_alias=AliasPath("nat", "rules", "entry"),
        default_factory=list,
    )

from pydantic import Field

from pa_api.xmlapi.types.utils import (
    List,
    XMLBaseModel,
)


class EDLMembers(XMLBaseModel):
    name: str
    total_valid: int = Field(alias="total-valid")
    total_ignored: int = Field(alias="total-ignored")
    total_invalid: int = Field(alias="total-invalid")
    members: List[str] = Field(alias="valid-members", default=list)

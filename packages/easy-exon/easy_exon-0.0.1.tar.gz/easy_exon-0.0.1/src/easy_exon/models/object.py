from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field

class ObjectAddress(BaseModel):
    postal_code:       Optional[str] = None
    region:            Optional[str] = None
    region_with_type:  Optional[str] = None
    city_type:         Optional[str] = None
    city:              Optional[str] = None
    city_with_type:    Optional[str] = None
    city_area:         Optional[str] = None
    street:            Optional[str] = None
    house:             Optional[str] = None
    projectAddressValue: Optional[str] = Field(default=None, alias="projectAddressValue")

    model_config = {
        "populate_by_name": True,
    }


class Object(BaseModel):
    id:               str
    category:         Optional[str]                 = None
    hashTags:         Optional[List[str]]           = None
    image:            Optional[str]                 = None
    name:             Optional[str]                 = None
    status:           Optional[str]                 = None
    projectAddress:   Optional[ObjectAddress]      = None
    integrationType:  Optional[str]                 = None
    dsCode:           Optional[str]                 = None
    gis:              Optional[bool]                = None

    model_config = {
        "populate_by_name": True,
    }

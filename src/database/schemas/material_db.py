from typing import Optional, Annotated
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository


class MaterialDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    description: str
    f125: Annotated[float, Field(alias="125")]
    f250: Annotated[float, Field(alias="250")]
    f500: Annotated[float, Field(alias="500")]
    f1000: Annotated[float, Field(alias="1000")]
    f2000: Annotated[float, Field(alias="2000")]
    f4000: Annotated[float, Field(alias="4000")]

    class Config:
        populate_by_name = True  # ermöglicht Zugriff auf _125 via "125"


class MaterialRepository(AsyncAbstractRepository[MaterialDbModel]):
    class Meta:
        collection_name = "materials"

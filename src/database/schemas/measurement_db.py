from typing import Optional, List
from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository

from models import AcousticParameters

class MeasurementDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    ownerToken: str
    values: List[List[AcousticParameters]]

class MeasurementRepository(AsyncAbstractRepository[MeasurementDbModel]):
    class Meta:
        collection_name = "measurements"
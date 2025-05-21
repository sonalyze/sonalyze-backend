from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository

from models import AcousticParameters

class MeasurementDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    ownerToken: str
    values: List[List[AcousticParameters]]
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class MeasurementRepository(AsyncAbstractRepository[MeasurementDbModel]):
    class Meta:
        collection_name = "measurements"
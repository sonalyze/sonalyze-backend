from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository

from models import AcousticParameters
from models.scene import RoomScene

class RoomDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    ownerToken: str
    room: RoomScene
    simulation: Optional[List[List[AcousticParameters]] ] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class RoomRepository(AsyncAbstractRepository[RoomDbModel]):
    class Meta:
        collection_name = "rooms"
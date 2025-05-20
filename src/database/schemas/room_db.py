from typing import Optional, List
from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository

from models import AcousticParameters
from models.scene import RoomScene

class RoomDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    name: str
    ownerToken: str
    room: Optional[RoomScene] = None
    simulation: Optional[List[List[AcousticParameters]] ] = None

class RoomRepository(AsyncAbstractRepository[RoomDbModel]):
    class Meta:
        collection_name = "rooms"
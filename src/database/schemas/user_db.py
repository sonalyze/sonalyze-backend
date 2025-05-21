from typing import Optional, List
from pydantic import BaseModel
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository

from models import AcousticParameters

class UserDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    rooms: List[str] = []
    measurements: List[str] = []

class UserRepository(AsyncAbstractRepository[UserDbModel]):
    class Meta:
        collection_name = "users"
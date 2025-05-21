from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId, AsyncAbstractRepository

class UserDbModel(BaseModel):
    id: Optional[PydanticObjectId] = None
    rooms: List[str] = []
    measurements: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UserRepository(AsyncAbstractRepository[UserDbModel]):
    class Meta:
        collection_name = "users"
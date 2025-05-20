from pydantic import BaseModel, Field

from api.models.room_scene import RestRoomScene
from typing import List


class CreateRoom(BaseModel):
    name: str = Field(..., title="Room name", description="Name of the room to create")
    scene: RestRoomScene = Field(..., title="Room scene", description="Scene of the room to create")

class UpdateRoom(BaseModel):
    name: str = Field(..., title="Room name", description="Updated name")

class GetIds(BaseModel):
    ids: List[str] = Field(..., title="Ids", description="Ids to select")

class UpdateScene(BaseModel):
    scene: RestRoomScene = Field(..., title="Room scene", description="Updated scene")
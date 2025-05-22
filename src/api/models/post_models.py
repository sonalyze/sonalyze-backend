from pydantic import BaseModel, Field

from api.models.room_scene import RestRoomScene


class CreateRoom(BaseModel):
    name: str = Field(..., title="Room name", description="Name of the room to create")
    scene: RestRoomScene = Field(..., title="Room scene", description="Scene of the room to create")

class UpdateRoom(BaseModel):
    name: str = Field(..., title="Room name", description="Updated name")

class UpdateScene(BaseModel):
    scene: RestRoomScene = Field(..., title="Room scene", description="Updated scene")

class PostUserIds(BaseModel):
    token: str = Field(..., title="User token", description="User token")
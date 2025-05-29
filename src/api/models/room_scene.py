from pydantic import Field, BaseModel
from typing import List

from models.scene import RoomScene


class RestRoomScene(RoomScene):
    roomId: str = Field(..., title="Room ID", description="ID of the room")
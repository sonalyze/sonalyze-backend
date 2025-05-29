from pydantic import BaseModel, Field

from typing import List


class Dimensions(BaseModel):
    width: float = Field(..., title="Width", description="Width of the room in meters")
    height: float = Field(..., title="Height", description="Height of the room in meters")
    depth: float = Field(..., title="Depth", description="Depth of the room in meters")

class Materials(BaseModel):
    east: str = Field(..., title="East wall material", description="Material of the east wall")
    west: str = Field(..., title="West wall material", description="Material of the west wall")
    north: str = Field(..., title="North wall material", description="Material of the north wall")
    south: str = Field(..., title="South wall material", description="Material of the south wall")
    ceiling: str = Field(..., title="Ceiling material", description="Material of the ceiling")
    floor: str = Field(..., title="Floor material", description="Material of the floor")

class Vector2(BaseModel):
    x: float = Field(..., title="X coordinate", description="X coordinate of the vector")
    y: float = Field(..., title="Y coordinate", description="Y coordinate of the vector")

class Vector3(BaseModel):
    x: float = Field(..., title="X coordinate", description="X coordinate of the vector")
    y: float = Field(..., title="Y coordinate", description="Y coordinate of the vector")
    z: float = Field(..., title="Z coordinate", description="Z coordinate of the vector")

class Furniture(BaseModel):
    height: float = Field(..., title="Height", description="Height of the furniture in meters")
    points: List[Vector2] = Field(..., title="Points", description="List of points defining the furniture's position in the room")

class RoomScene(BaseModel):
    dimensions: Dimensions = Field(..., title="Room dimensions", description="Dimensions of the room")
    materials: Materials = Field(..., title="Room materials", description="Materials of the room")
    furniture: List[Furniture] = Field(..., title="Furniture", description="List of furniture in the room")
    microphones: List[Vector3] = Field(..., title="Microphones", description="List of microphone positions in the room")
    speakers: List[Vector3] = Field(..., title="Speakers", description="List of speaker positions in the room")
from pydantic import BaseModel, Field

class Room(BaseModel):
    id: str
    name: str = Field(..., title="Room name", description="Name of the room")
    hasSimulation: bool = Field(..., title="Has simulation", description="Whether the room has existing simulation data or not")
    isOwner: bool = Field(..., title="Is owner", description="Whether the user is the owner of the room or not")
    lastUpdatedAt: str = Field(..., title="Last updated at", description="Last time the room was updated")
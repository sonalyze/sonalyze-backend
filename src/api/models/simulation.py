from pydantic import BaseModel, Field
from typing import List
from models import AcousticParameters


class Simulation(BaseModel):
    roomId: str = Field(..., title="Room ID", description="Id of the room the simulation belongs to")
    values: List[List[AcousticParameters]] = Field(..., title="Acoustic parameters", description="List of Acoustic parameters")
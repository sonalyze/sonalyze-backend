from pydantic import Field, BaseModel
from typing import List

from models import AcousticParameters

class Measurement(BaseModel):
    id: str = Field(..., title="Measurement ID", description="Unique identifier for the measurement")
    name: str = Field(..., title="Measurement name", description="Name of the measurement")
    createdAt: str = Field(..., title="Created at", description="Timestamp when the measurement was created")
    isOwner: bool = Field(..., title="Is owner", description="Whether the user is the owner of the measurement or not")
    values: List[List[AcousticParameters]] = Field(..., title="Acoustic parameters", description="List of acoustic parameters for the measurement")
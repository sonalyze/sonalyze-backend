from pydantic import BaseModel, Field
from typing import List

class AcousticParameters(BaseModel):
    rt60: List[float] = Field(..., title="RT60", description="RT60 values for different frequencies in seconds")
    c50: List[float] = Field(..., title="C50", description="C50 values for different frequencies in decibels")
    c80: List[float] = Field(..., title="C80", description="C80 values for different frequencies in decibels")
    g: List[float] = Field(..., title="G", description="G values for different frequencies in decibels")
    d50: List[float] = Field(..., title="D50", description="D50 values for different frequencies in decibels")
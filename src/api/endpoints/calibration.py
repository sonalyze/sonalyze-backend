from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import numpy as np

from src.services.calibration_utils import calculate_latency

router = APIRouter()

class CalibrationPayload(BaseModel):
    sampleRate: int
    original: List[float]
    recorded: List[float]

@router.post("/calibration/latency")
async def latency_endpoint(data: CalibrationPayload):
    original = np.array(data.original, dtype=np.float32)
    recorded = np.array(data.recorded, dtype=np.float32)
    result = calculate_latency(original, recorded, data.sampleRate)
    return result
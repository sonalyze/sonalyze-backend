# PYTHONPATH=src uv run uvicorn src.main:app --reload

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import numpy as np
from scipy.signal.windows import tukey
from scipy.ndimage import uniform_filter1d

router = APIRouter()

class AudioPayload(BaseModel):
    sampleRate: int
    signal: List[float]

@router.post("/impulse-response")
async def analyze_impulse_response(data: AudioPayload):
    fs = data.sampleRate
    h = np.array(data.signal, dtype=np.float32)

    # Fensterung
    window = tukey(len(h), 0.1)
    h_windowed = h * window

    # Schroeder-Integration
    energy = np.cumsum(h_windowed[::-1]**2)[::-1]
    energy_db = 10 * np.log10(energy / np.max(energy))
    energy_db_smooth = uniform_filter1d(energy_db, size=int(0.01 * fs))

    try:
        t = np.arange(len(energy_db_smooth)) / fs
        t1 = t[np.where(energy_db_smooth <= -5)[0][0]]
        t2 = t[np.where(energy_db_smooth <= -35)[0][0]]
        T30 = 2 * (t2 - t1)
    except IndexError:
        T30 = None

    return {
        "samples": len(h),
        "duration_s": round(len(h) / fs, 3),
        "T30": round(T30, 3) if T30 else "N/A"
    }

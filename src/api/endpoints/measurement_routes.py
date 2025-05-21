from fastapi import APIRouter
from typing import List

from fastapi.params import Depends

from api.models.measurement import RestMeasurement
from services.auth_service import get_token_header

router = APIRouter()

@router.get("/", response_model=List[RestMeasurement], tags=["measurements"])
async def get_measurements(token: Depends = Depends(get_token_header)) -> List[RestMeasurement]:
    return []

@router.delete("/{id}", tags=["measurements"])
async def delete_measurement(id: str, token: Depends = Depends(get_token_header)) -> None:
    return None

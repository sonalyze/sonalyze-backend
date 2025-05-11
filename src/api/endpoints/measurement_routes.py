from fastapi import APIRouter
from typing import List

from fastapi.params import Depends

from api.models.measurement import Measurement
from api.models.post_models import GetIds
from services.auth_service import get_token_header

router = APIRouter()

@router.put("/", tags=["measurements"])
async def get_measurements(body: GetIds, token = Depends(get_token_header)) -> List[Measurement]:
    return []

@router.delete("/{id}", tags=["measurements"])
async def delete_measurement(id: str, token = Depends(get_token_header)) -> None:
    return None

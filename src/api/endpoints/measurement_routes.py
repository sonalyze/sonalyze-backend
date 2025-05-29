from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List, Annotated

from fastapi.params import Depends

from api.models.measurement import RestMeasurement
from database.engine import DataContext, get_db
from services.auth_service import get_token_header
from services.mapper_service import map_measurement_db_to_rest_measurement

router = APIRouter()

@router.get("/", response_model=List[RestMeasurement], tags=["measurements"])
async def get_measurements(
        token: Annotated[str, Depends(get_token_header)],
        data_context: Annotated[DataContext, Depends(get_db)]
) -> List[RestMeasurement]:
    """
    Get all measurements for the calling user.
    """
    user = await data_context.users.find_one_by_id(ObjectId(token))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    measurement_ids = [ObjectId(s) for s in user.measurements]
    measurements_db = await data_context.measurements.find_by({'_id': {'$in': measurement_ids}})
    measurements: List[RestMeasurement] = []
    for measurement_db in measurements_db:
        measurements.append(map_measurement_db_to_rest_measurement(measurement_db, token))
    return measurements

@router.delete("/{id}", tags=["measurements"])
async def delete_measurement(
        measurement_id: str,
        token: Annotated[str, Depends(get_token_header)],
        data_context: Annotated[DataContext, Depends(get_db)]
) -> None:
    """
    Delete a measurement owned by the calling user.
    """
    measurement = await data_context.measurements.find_one_by_id(ObjectId(measurement_id))
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    if measurement.ownerToken != token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await data_context.measurements.delete_by_id(measurement_id)

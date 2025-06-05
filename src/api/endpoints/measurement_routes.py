from fastapi import APIRouter, HTTPException
from typing import List, Annotated

from fastapi.params import Depends

from api.models.measurement import RestMeasurement
from database.engine import DataContext, get_db
from services.auth_service import get_token_header, HttpObjectId
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
    user = await data_context.users.find_one_by_id(HttpObjectId(token))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    measurement_ids = [HttpObjectId(s) for s in user.measurements]
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
    measurement = await data_context.measurements.find_one_by_id(HttpObjectId(measurement_id))
    if not measurement:
        raise HTTPException(status_code=404, detail="Measurement not found")
    if measurement.ownerToken != token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await data_context.measurements.delete_by_id(measurement_id)

@router.get("/imported/{measurement_id}", tags=["measurement"])
async def import_measurement(
        measurement_id: str,
        token: Annotated[str, Depends(get_token_header)],
        data_context: Annotated[DataContext, Depends(get_db)],
) -> RestMeasurement | None:
    """
    Get a certain measurement based on its ID.
    Adds the measurement to the current user's history.
    """
    measurement_db = await data_context.measurements.find_one_by_id(HttpObjectId(measurement_id))
    if not measurement_db:
        raise HTTPException(status_code=404, detail="Measurement not found")

    user_db = await data_context.users.find_one_by_id(HttpObjectId(token))
    assert user_db is not None
    if measurement_id not in user_db.measurements:
        user_db.measurements.append(str(measurement_db.id))
        await data_context.users.save(user_db)

    return map_measurement_db_to_rest_measurement(measurement_db, token)

@router.delete("/imported/{measurement_id}", tags=["measurement"])
async def remove_imported_measurement(
        measurement_id: str,
        token: Annotated[str, Depends(get_token_header)],
        data_context: Annotated[DataContext, Depends(get_db)],
) -> None:
    """
    Removes a measurement from the current user's history.
    """

    user_db = await data_context.users.find_one_by_id(HttpObjectId(token))
    assert user_db is not None

    if measurement_id in user_db.measurements:
        user_db.measurements.remove(str(measurement_id))
        await data_context.users.save(user_db)
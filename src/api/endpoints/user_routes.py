import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List, Annotated

from fastapi.params import Depends

from api.models.measurement import RestMeasurement
from api.models.post_models import PostUserIds
from api.models.simulation import Simulation
from database.engine import DataContext, get_db
from database.schemas.user_db import UserDbModel
from services.auth_service import get_token_header
from services.mapper_service import map_measurement_db_to_rest_measurement

logger = logging.getLogger(__name__)
router = APIRouter()

@router.put("/register", tags=["user"])
async def register_user(
        body: PostUserIds,
        data_context: Annotated[DataContext, Depends(get_db)]
) -> None:
    user = UserDbModel(
        id=ObjectId(body.token),
        rooms=[],
        measurements=[]
    )
    await data_context.users.save(user)

@router.put("/migrate", tags=["user"])
async def migrate_user(
        body: PostUserIds,
        token: Annotated[str, Depends(get_token_header)],
        data_context: Annotated[DataContext, Depends(get_db)]
) -> None:
    old_user = await data_context.users.find_one_by_id(ObjectId(token))
    if old_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    new_user = await data_context.users.find_one_by_id(ObjectId(body.token))
    if new_user is None or old_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for room in old_user.rooms:
        new_user.rooms.append(room)
        logger.warning(room)
        room_db = await data_context.rooms.find_one_by_id(ObjectId(room))
        if room_db is None:
            raise HTTPException(status_code=404, detail="Room not found")
        room_db.ownerToken = body.token
        await data_context.rooms.save(room_db)

    for measurement in old_user.measurements:
        new_user.measurements.append(measurement)
        measurement_db = await data_context.measurements.find_one_by_id(ObjectId(measurement))
        assert measurement_db is not None
        measurement_db.ownerToken = body.token
        await data_context.measurements.save(measurement_db)

    await data_context.users.save(new_user)
    await data_context.users.delete(old_user)

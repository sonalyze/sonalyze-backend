import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import Annotated

from fastapi.params import Depends

from api.models.post_models import PostUserIds
from database.engine import DataContext, get_db
from database.schemas.user_db import UserDbModel
from services.auth_service import get_token_header

logger = logging.getLogger(__name__)
router = APIRouter()

@router.put("/register", tags=["user"])
async def register_user(
        body: PostUserIds,
        data_context: Annotated[DataContext, Depends(get_db)]
) -> None:
    """
    Registers a new user.
    """
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
    """
    Migrate one user account to another existing user.
    Changes ownership of all rooms and measurements.
    Deletes the migrated-from user.
    """
    old_user = await data_context.users.find_one_by_id(ObjectId(token))
    if old_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    new_user = await data_context.users.find_one_by_id(ObjectId(body.token))
    if new_user is None or old_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    for room in old_user.rooms:
        if not room in new_user.rooms:
            new_user.rooms.append(room)
        room_db = await data_context.rooms.find_one_by_id(ObjectId(room))
        assert room_db is not None
        if room_db.ownerToken == str(old_user.id):
            room_db.ownerToken = body.token
        await data_context.rooms.save(room_db)

    for measurement in old_user.measurements:
        if not measurement in new_user.measurements:
            new_user.measurements.append(measurement)
        measurement_db = await data_context.measurements.find_one_by_id(ObjectId(measurement))
        assert measurement_db is not None
        if measurement_db.ownerToken == str(old_user.id):
            measurement_db.ownerToken = body.token
        await data_context.measurements.save(measurement_db)

    await data_context.users.save(new_user)
    await data_context.users.delete(old_user)

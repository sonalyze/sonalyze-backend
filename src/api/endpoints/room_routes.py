import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException
from typing import List, Annotated

from fastapi.params import Depends

from api.models.post_models import UpdateRoom, CreateRoom, UpdateScene
from api.models.room import Room
from api.models.room_scene import RestRoomScene
from api.models.simulation import Simulation
from database.engine import DataContext, get_db
from database.schemas.room_db import RoomDbModel
from services.auth_service import get_token_header, HttpObjectId
from services.mapper_service import (
    map_room_db_to_room,
    map_room_db_to_rest_room_scene,
    map_update_scene_to_room_db,
    map_room_db_to_simulation,
)
from services.simulation_service import simulate_room

logger = logging.getLogger("uvicorn.info")

router = APIRouter()


@router.get("/", response_model=List[Room], tags=["room"])
async def get_rooms(
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> List[Room]:
    """
    Get general info about all rooms of the calling user.
    """
    user = await data_context.users.find_one_by_id(HttpObjectId(token))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_ids = [HttpObjectId(s) for s in user.rooms]
    rooms_db = await data_context.rooms.find_by({"_id": {"$in": room_ids}})
    rooms: List[Room] = []
    for room_db in rooms_db:
        rooms.append(map_room_db_to_room(room_db, token))

    return list(rooms) if rooms else []


@router.delete("/{room_id}", tags=["room"])
async def delete_room(
    room_id: str,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> None:
    """
    Delete a room owned by the calling user.
    """
    room = await data_context.rooms.find_one_by_id(HttpObjectId(room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await data_context.rooms.delete_by_id(room.id)


@router.post("/", tags=["room"])
async def create_room(
    body: CreateRoom,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> Room | None:
    """
    Create a new room with a scene.
    """
    room_db: RoomDbModel = RoomDbModel(
        name=body.name, ownerToken=token, room=body.scene
    )
    await data_context.rooms.save(room_db)
    user = await data_context.users.find_one_by_id(HttpObjectId(token))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    user.rooms.append(str(room_db.id))
    await data_context.users.save(user)

    return map_room_db_to_room(room_db, token)


@router.put("/{room_id}", tags=["room"])
async def update_room(
    room_id: str,
    body: UpdateRoom,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> None:
    """
    Update the general info of a room.
    Requires ownership of the room.
    """
    room_db = await data_context.rooms.find_one_by_id(HttpObjectId(room_id))
    if not room_db:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room_db.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_db.name = body.name
    room_db.updated_at = datetime.now()
    await data_context.rooms.save(room_db)


@router.get("/imported/{room_id}", tags=["room"])
async def import_room(
    room_id: str,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> Room | None:
    """
    Get a certain room based on its ID.
    Adds the room to the current user's history.
    """
    room_db = await data_context.rooms.find_one_by_id(HttpObjectId(room_id))
    if not room_db:
        raise HTTPException(status_code=404, detail="Room not found")

    user_db = await data_context.users.find_one_by_id(HttpObjectId(token))
    assert user_db is not None
    if room_id not in user_db.rooms:
        user_db.rooms.append(str(room_db.id))
        await data_context.users.save(user_db)

    return map_room_db_to_room(room_db, token)


@router.delete("/imported/{room_id}", tags=["room"])
async def remove_imported_room(
    room_id: str,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> None:
    """
    Remove a room from the current user's history.
    """

    user_db = await data_context.users.find_one_by_id(HttpObjectId(token))
    assert user_db is not None
    if room_id in user_db.rooms:
        user_db.rooms.remove(str(room_id))
        await data_context.users.save(user_db)


@router.get("/{room_id}/scene", response_model=RestRoomScene, tags=["scene"])
async def get_room_scene(
    room_id: str, data_context: Annotated[DataContext, Depends(get_db)]
) -> RestRoomScene | None:
    """
    Get the 3D-Scene of the given room.
    """
    room_db = await data_context.rooms.find_one_by_id(HttpObjectId(room_id))
    if not room_db or not room_db.room:
        raise HTTPException(status_code=404, detail="Room not found")

    return map_room_db_to_rest_room_scene(room_db)


@router.put("/{room_id}/scene", tags=["scene"])
async def update_room_scene(
    room_id: str,
    scene: UpdateScene,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> None:
    """
    Update the 3D-Scene of the given room.
    Requires ownership of the room.
    """
    room_db = await data_context.rooms.find_one_by_id(HttpObjectId(room_id))
    if not room_db or not room_db.room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room_db.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_db = map_update_scene_to_room_db(room_db, scene)
    room_db.updated_at = datetime.now()
    await data_context.rooms.save(room_db)


@router.get(
    "/{room_id}/simulation/result", response_model=Simulation, tags=["simulation"]
)
async def get_simulation_result(
    room_id: str, data_context: Annotated[DataContext, Depends(get_db)]
) -> Simulation | None:
    """
    Get the existing simulation result of a room.
    """
    room_db = await data_context.rooms.find_one_by_id(HttpObjectId(room_id))
    if not room_db or not room_db.simulation:
        raise HTTPException(status_code=404, detail="Room not found")

    return map_room_db_to_simulation(room_db)


@router.get("/{room_id}/simulation", tags=["simulation"])
async def do_simulation(
    room_id: str,
    token: Annotated[str, Depends(get_token_header)],
    data_context: Annotated[DataContext, Depends(get_db)],
) -> Simulation | None:
    room_scene: RestRoomScene | None = await get_room_scene(room_id, data_context)
    if room_scene is None:
        raise HTTPException(status_code=404, detail="Room scene not found")
    result = await simulate_room(room_scene, data_context)
    return result

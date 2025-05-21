import logging

from bson import ObjectId
from fastapi import APIRouter, HTTPException
from typing import List, Annotated

from fastapi.params import Depends

from api.models.post_models import UpdateRoom, CreateRoom, UpdateScene
from api.models.room import Room
from api.models.room_scene import RestRoomScene
from api.models.simulation import Simulation
from database.engine import DataContext, get_db
from database.schemas.room_db import RoomDbModel
from services.auth_service import get_token_header
from services.mapper_service import map_room_db_to_room, map_room_db_to_rest_room_scene, map_update_scene_to_room_db, \
    map_room_db_to_simulation

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Room], tags=["room"])
async def get_rooms(token: Annotated[str, Depends(get_token_header)], data_context: Annotated[DataContext, Depends(get_db)]) -> List[Room]:
    user = await data_context.users.find_one_by_id(ObjectId(token))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_ids = [ObjectId(s) for s in user.rooms]
    rooms_db = await data_context.rooms.find_by({'_id': {'$in': room_ids}})
    rooms: List[Room] = []
    for room_db in rooms_db:
        rooms.append(map_room_db_to_room(room_db, token))

    return list(rooms) if rooms else []

@router.delete("/{room_id}", tags=["room"])
async def delete_room(room_id: str, token: Annotated[str, Depends(get_token_header)],
                      data_context: Annotated[DataContext, Depends(get_db)]) -> None:
    room = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await data_context.rooms.delete_by_id(room.id)

@router.post("/", tags=["room"])
async def create_room(body: CreateRoom, token: Annotated[str, Depends(get_token_header)],
                      data_context: Annotated[DataContext, Depends(get_db)]) -> Room | None:
    room_db: RoomDbModel = RoomDbModel(name=body.name,
                                       ownerToken=token,
                                       room=body.scene)
    await data_context.rooms.save(room_db)

    return map_room_db_to_room(room_db, token)

@router.put("/{room_id}", tags=["room"])
async def update_room(room_id: str, body: UpdateRoom, token: Annotated[str, Depends(get_token_header)],
                      data_context: Annotated[DataContext, Depends(get_db)]) -> None:
    room_db = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room_db:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room_db.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_db.name = body.name
    await data_context.rooms.save(room_db)

@router.get("/{room_id}/scene", response_model=RestRoomScene, tags=["scene"])
async def get_room_scene(room_id: str, data_context: Annotated[DataContext, Depends(get_db)]) -> RestRoomScene | None:
    room_db = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room_db or not room_db.room:
        raise HTTPException(status_code=404, detail="Room not found")

    return map_room_db_to_rest_room_scene(room_db)

@router.put("/{room_id}/scene", tags=["scene"])
async def update_room_scene(room_id: str, scene: UpdateScene, token: Annotated[str, Depends(get_token_header)],
                            data_context: Annotated[DataContext, Depends(get_db)]) -> None:
    room_db = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room_db or not room_db.room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room_db.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_db = map_update_scene_to_room_db(room_db, scene)
    await data_context.rooms.save(room_db)

@router.get("/{room_id}/simulation/result", response_model=Simulation, tags=["simulation"])
async def get_simulation_result(room_id: str,  data_context: Annotated[DataContext, Depends(get_db)]) -> Simulation | None:
    room_db = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room_db or not room_db.simulation:
        raise HTTPException(status_code=404, detail="Room not found")

    return map_room_db_to_simulation(room_db)

@router.get("/{room_id}/simulation", tags=["simulation"])
async def do_simulation(room_id: str, token: Annotated[str, Depends(get_token_header)],
                        data_context: Annotated[DataContext, Depends(get_db)]) -> Simulation | None:

    return None

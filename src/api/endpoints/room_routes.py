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
from services.auth_service import get_token_header

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
        room = Room(id=str(room_db.id),
                    name=room_db.name,
                    isOwner=True if room_db.ownerToken == token else False,
                    hasSimulation=False if room_db.simulation is None else True,
                    lastUpdatedAt="123")
        rooms.append(room)

    return list(rooms) if rooms else []

@router.delete("/{room_id}", tags=["room"])
async def delete_room(room_id: str, token: Annotated[str, Depends(get_token_header)], data_context: Annotated[DataContext, Depends(get_db)]) -> None:
    room = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    await data_context.rooms.delete_by_id(room.id)

@router.post("/", tags=["room"])
async def create_room(name: str, body: CreateRoom, token: Depends = Depends(get_token_header)) -> Room | None:
    return None

@router.put("/{room_id}", tags=["room"])
async def update_room(room_id: str, body: UpdateRoom, token: Annotated[str, Depends(get_token_header)], data_context: Annotated[DataContext, Depends(get_db)]) -> None:
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
    scene: RestRoomScene = RestRoomScene(roomId=room_id,
                                         speakers=room_db.room.speakers,
                                         furniture=room_db.room.furniture,
                                         materials=room_db.room.materials,
                                         dimensions=room_db.room.dimensions,
                                         microphones=room_db.room.microphones)
    return scene

@router.put("/{room_id}/scene", tags=["scene"])
async def update_room_scene(room_id: str, scene: UpdateScene, token: Annotated[str, Depends(get_token_header)], data_context: Annotated[DataContext, Depends(get_db)]) -> None:
    room_db = await data_context.rooms.find_one_by_id(ObjectId(room_id))
    if not room_db or not room_db.room:
        raise HTTPException(status_code=404, detail="Room not found")
    if not room_db.ownerToken == token:
        raise HTTPException(status_code=401, detail="Unauthorized")

    room_db.room.speakers = scene.scene.speakers
    room_db.room.furniture = scene.scene.furniture
    room_db.room.materials = scene.scene.materials
    room_db.room.dimensions = scene.scene.dimensions
    room_db.room.microphones = scene.scene.microphones
    await data_context.rooms.save(room_db)

@router.get("/{room_id}/simulation/result", tags=["simulation"])
async def get_simulation_result(room_id: str) -> Simulation | None:
    return None

@router.get("/{room_id}/simulation", tags=["simulation"])
async def do_simulation(room_id: str, token: Depends = Depends(get_token_header)) -> Simulation | None:
    return None

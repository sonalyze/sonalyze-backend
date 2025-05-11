from fastapi import APIRouter
from typing import List

from fastapi.params import Depends

from api.models.post_models import UpdateRoom, CreateRoom, GetIds, UpdateScene
from api.models.room import Room
from api.models.room_scene import RoomScene
from api.models.simulation import Simulation
from services.auth_service import get_token_header

router = APIRouter()

@router.put("/", tags=["room"])
async def get_rooms(body: GetIds, token: str = Depends(get_token_header)) -> List[Room]:
    return []

@router.delete("/{room_id}", tags=["room"])
async def delete_room(room_id: str, token: str = Depends(get_token_header)) -> None:
    return None

@router.post("/", tags=["room"])
async def create_room(name: str, body: CreateRoom, token: str = Depends(get_token_header)) -> Room:
    return None

@router.put("/{room_id}", tags=["room"])
async def update_room(room_id: str, body: UpdateRoom, token: str = Depends(get_token_header)) -> None:
    return None

@router.get("/{room_id}/scene", tags=["scene"])
async def get_room_scene(room_id: str) -> RoomScene:
    return None

@router.put("/{room_id}/scene", tags=["scene"])
async def update_room_scene(room_id: str, scene: UpdateScene, token: str = Depends(get_token_header)) -> None:
    return None

@router.get("/{room_id}/simulation/result", tags=["simulation"])
async def get_simulation_result(room_id: str) -> Simulation:
    return None

@router.get("/{room_id}/simulation", tags=["simulation"])
async def do_simulation(room_id: str, token: str = Depends(get_token_header)) -> Simulation:
    return None

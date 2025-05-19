from fastapi.params import Depends

from database.engine import DataContext, get_db
from database.schemas.room_db import RoomDbModel
from .endpoints import room_routes, measurement_routes
from fastapi import APIRouter
import logging

logger = logging.getLogger("uvicorn.info")

router = APIRouter()

router.include_router(room_routes.router, prefix="/room", tags=["room"])
router.include_router(measurement_routes.router, prefix="/measurements", tags=["measurements"])


@router.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    logger.warning("Root endpoint accessed")
    return {"message": "welcome to aal :)"}

@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}

@router.get("/test", response_model=RoomDbModel,tags=["test"])
async def test(repo: DataContext = Depends(get_db)) -> RoomDbModel:
    res = await repo.rooms.find_one_by({})
    return res
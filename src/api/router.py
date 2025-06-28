from .endpoints import room_routes, measurement_routes, user_routes
from fastapi import APIRouter
import logging

logger = logging.getLogger("uvicorn.info")

router = APIRouter()

router.include_router(room_routes.router, prefix="/room", tags=["room"])
router.include_router(measurement_routes.router, prefix="/measurements", tags=["measurements"])
router.include_router(user_routes.router, prefix="/users", tags=["user"])

@router.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    return {"message": "welcome to 🐍🌊 :)"}
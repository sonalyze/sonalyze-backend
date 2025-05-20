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
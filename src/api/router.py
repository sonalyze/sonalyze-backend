from .endpoints import rooms
from fastapi import APIRouter

router = APIRouter()

router.include_router(rooms.router, prefix="/rooms", tags=["root"])

@router.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    return {"message": "welcome to aal"}

@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
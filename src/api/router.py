from src.api.endpoints import test, impulse_response, calibration
from fastapi import APIRouter
import logging

logger = logging.getLogger("uvicorn.info")


router = APIRouter()

router.include_router(test.router, prefix="/test", tags=["test"])
router.include_router(impulse_response.router, prefix="", tags=["audio"])
router.include_router(calibration.router, tags=["calibration"])

@router.get("/", tags=["root"])
async def read_root() -> dict[str, str]:
    logger.warning("Root endpoint accessed")
    return {"message": "welcome to aal :)"}

@router.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
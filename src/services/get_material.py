from database.engine import DataContext, get_db
from database.schemas.material_db import MaterialDbModel
from pymongo.errors import PyMongoError
import logging
import re
from models.material import MaterialAbsorptionResult
from typing import Annotated
from fastapi import Depends

logger = logging.getLogger("uvicorn.info")


async def get_material_absorption(
    name: str, db: Annotated[DataContext, Depends(get_db)]
) -> MaterialAbsorptionResult:
    try:
        # Suche Materialbeschreibung via Regex
        material: MaterialDbModel | None = await db.materials.find_one_by(
            {"description": {"$regex": re.escape(name), "$options": "i"}}
        )

        if not material:
            raise ValueError(f"Material '{name}' nicht gefunden.")

        coeffs = [
            getattr(material, "f125", 0.0),
            getattr(material, "f250", 0.0),
            getattr(material, "f500", 0.0),
            getattr(material, "f1000", 0.0),
            getattr(material, "f2000", 0.0),
            getattr(material, "f4000", 0.0),
        ]

        return MaterialAbsorptionResult(
            name=material.description,
            coeffs=coeffs,
            center_freqs=[125, 250, 500, 1000, 2000, 4000],
        )

    except PyMongoError as e:
        raise RuntimeError(f"Datenbankfehler: {e}")


# How to use
# from database.engine import data_context
# material = await get_material_absorption("carpet", data_context)

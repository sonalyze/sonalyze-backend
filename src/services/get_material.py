from database.engine import DataContext
from database.schemas.material_db import MaterialDbModel
from pymongo.errors import PyMongoError

from typing import Any
import re


async def get_material_absorption(
    name: str, db: DataContext
) -> dict[str, list[Any | int]]:
    try:
        # Suche Materialbeschreibung via Regex
        material: MaterialDbModel | None = await db.materials.find_one_by(
            {"description": {"$regex": re.escape(name), "$options": "i"}}
        )

        if not material:
            raise ValueError(f"Material '{name}' nicht gefunden.")

        print(material)

        absorption = [
            getattr(material, "f125", 0),
            getattr(material, "f250", 0),
            getattr(material, "f500", 0),
            getattr(material, "f1000", 0),
            getattr(material, "f2000", 0),
            getattr(material, "f4000", 0),
        ]

        return {"absorption": absorption}

    except PyMongoError as e:
        raise RuntimeError(f"Datenbankfehler: {e}")


# How to use
# from database.engine import data_context
# material = await get_material_absorption("carpet", data_context)

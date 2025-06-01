from pymongo import MongoClient
from dotenv import dotenv_values
from typing import Any

# DB-Verbindung
env = dotenv_values("../../.env")
uri = f"mongodb://{env.get('DB_CONNECTION_STRING', '')}"
if not uri:
    raise ValueError("DB_CONNECTION_STRING is empty or missing in .env")

client: MongoClient[Any]
client = MongoClient(uri)
db = client["test_database"]
collection = db["materials"]


def get_material_json_from_db(name: str) -> dict[str, list[float]]:
    # Suche alle Materialien mit Beschreibung, die 'name' enthält (case-insensitive)
    result = collection.find_one({"description": {"$regex": name, "$options": "i"}})

    if not result:
        raise ValueError(f"Material '{name}' nicht gefunden.")

    # Frequenzwerte holen (Standard = 0, falls kein Wert vorhanden ist)
    absorption = [
        result.get("125", 0),
        result.get("250", 0),
        result.get("500", 0),
        result.get("1000", 0),
        result.get("2000", 0),
        result.get("4000", 0),
    ]

    return {"absorption": absorption}

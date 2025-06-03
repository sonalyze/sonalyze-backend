from dotenv import dotenv_values
from pathlib import Path
from typing import Generator
from pymongo import AsyncMongoClient

import logging

from database.schemas.measurement_db import MeasurementRepository
from database.schemas.room_db import RoomRepository
from database.schemas.user_db import UserRepository
from database.schemas.material_db import MaterialRepository


class DataContext:
    def __init__(self, mongo_client: AsyncMongoClient):  # type: ignore[type-arg]
        database = mongo_client.test_database
        self.rooms = RoomRepository(database)
        self.measurements = MeasurementRepository(database)
        self.users = UserRepository(database)
        self.materials = MaterialRepository(database)

    rooms: RoomRepository
    measurements: MeasurementRepository
    users: UserRepository
    materials: MaterialRepository


logger = logging.getLogger(__name__)


env_path = Path(__file__).resolve().parents[2] / ".env"
env = dotenv_values(env_path)
connection_string = env.get("DB_CONNECTION_STRING")

uri = f"mongodb://{connection_string}"
client: AsyncMongoClient = AsyncMongoClient(uri)  # type: ignore[type-arg]
data_context = DataContext(client)


def get_db() -> Generator[DataContext, None, None]:
    yield data_context

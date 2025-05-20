
from dotenv import dotenv_values
from typing import Generator
from pymongo import AsyncMongoClient

import logging

from database.schemas.measurement_db import MeasurementRepository
from database.schemas.room_db import RoomRepository
from database.schemas.user_db import UserRepository


class DataContext:
    def __init__(self, mongo_client: AsyncMongoClient): # type: ignore[type-arg]
        database = mongo_client.test_database
        self.rooms = RoomRepository(database)
        self.measurements = MeasurementRepository(database)
        self.users = UserRepository(database)
    rooms: RoomRepository
    measurements: MeasurementRepository
    users: UserRepository

logger = logging.getLogger(__name__)

connection_string = dotenv_values(".env")["DB_CONNECTION_STRING"] or ""

uri = f"mongodb://{connection_string}"
client: AsyncMongoClient = AsyncMongoClient(uri) # type: ignore[type-arg]
data_context = DataContext(client)


def get_db() -> Generator[DataContext, None, None]:
    yield data_context
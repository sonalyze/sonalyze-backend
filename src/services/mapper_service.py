from bson import ObjectId
from rich.measure import Measurement

from api.models.measurement import RestMeasurement
from api.models.post_models import CreateRoom, UpdateScene
from api.models.room import Room
from api.models.room_scene import RestRoomScene
from api.models.simulation import Simulation
from database.schemas.measurement_db import MeasurementDbModel
from database.schemas.room_db import RoomDbModel


def map_room_db_to_room(room_db: RoomDbModel, token: str) -> Room:
    """
    Maps a RoomDbModel instance to a Room API model.
    """
    return Room(
        id=str(room_db.id),
        name=room_db.name,
        isOwner=(room_db.ownerToken == token),
        hasSimulation=(room_db.simulation is not None),
        lastUpdatedAt=room_db.updated_at.isoformat()
    )


def map_create_room_to_room_db(body: CreateRoom, token: str) -> RoomDbModel:
    """
    Maps a CreateRoom request to a new RoomDbModel for persistence.
    """
    return RoomDbModel(
        name=body.name,
        ownerToken=token,
        room=body.scene
    )


def map_room_db_to_rest_room_scene(room_db: RoomDbModel) -> RestRoomScene:
    """
    Maps the scene portion of a RoomDbModel to RestRoomScene.
    """
    return RestRoomScene(
        roomId=str(room_db.id),
        speakers=room_db.room.speakers,
        furniture=room_db.room.furniture,
        materials=room_db.room.materials,
        dimensions=room_db.room.dimensions,
        microphones=room_db.room.microphones
    )


def map_update_scene_to_room_db(room_db: RoomDbModel, scene: UpdateScene) -> RoomDbModel:
    """
    Applies an UpdateScene request to the RoomDbModel's scene.
    """
    room_db.room.speakers = scene.scene.speakers
    room_db.room.furniture = scene.scene.furniture
    room_db.room.materials = scene.scene.materials
    room_db.room.dimensions = scene.scene.dimensions
    room_db.room.microphones = scene.scene.microphones
    return room_db


def map_room_db_to_simulation(room_db: RoomDbModel) -> Simulation:
    """
    Maps a RoomDbModel's simulation data to the Simulation API model.
    """
    return Simulation(
        roomId=str(room_db.id),
        values=room_db.simulation or []
    )

def map_measurement_db_to_rest_measurement(measurement_db: MeasurementDbModel, token: str ) -> RestMeasurement:
    """
    Maps a Measurement DB model to the Measurement API model.
    """
    return RestMeasurement(
        id=str(measurement_db.id),
        isOwner=True if measurement_db.ownerToken == token else False,
        values=measurement_db.values,
        createdAt=measurement_db.created_at.isoformat(),
        name=measurement_db.name
    )

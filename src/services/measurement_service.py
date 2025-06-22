import asyncio
import logging

from socketio import AsyncServer
from typing import List, Dict
from sio.models import Lobby, RecordData

lobbies: Dict[str, Lobby] = {}
measurement_tasks: dict[str, asyncio.Task] = {} # type: ignore
measurement_queues: dict[str, asyncio.Queue[RecordData]] = {}

logger = logging.getLogger("uvicorn.info")

async def measurement_controller(sio: AsyncServer, lobby: Lobby) -> None:
    await sio.emit("start_measurement", {}, to=lobby.lobby_id)
    measurement_queues[lobby.lobby_id] = asyncio.Queue()
    await asyncio.sleep(1)
    data_list: List[List[RecordData]] = []

    for i in range(lobby.repetitions):
        logger.info(f"measurement cycle {i} for lobby {lobby.lobby_id} started")
        await sio.emit("start_recording", {}, to=lobby.lobby_id)
        await asyncio.sleep(1)
        for speaker in lobby.speakers:
            await sio.emit("play_sound", {}, to=speaker.sid)
            await asyncio.sleep(1)

        await sio.emit("end_recording", {}, to=lobby.lobby_id)

        record_data: List[RecordData] = []

        logger.info(f"Lobby {lobby.lobby_id} waiting for recorded data...")
        while len(record_data) < len(measurement_queues):
            data = await measurement_queues[lobby.lobby_id].get()

            record_data.append(data)

        logger.info(f"Lobby {lobby.lobby_id} received recorded data: {len(record_data)}")
        data_list.append(record_data)

        if i < (lobby.repetitions - 1):
            await asyncio.sleep(lobby.delay)

    await sio.emit("end_measurement", {}, to=lobby.lobby_id)

    # TODO do calculations, data_list contains recording files -> index 0 has list of first cycle, and so on
    # TODO lobby.distances has distances between any mic and any speaker in map in speaker -> mic -> distance format

    await asyncio.sleep(2)
    logger.info(f"Lobby {lobby.lobby_id} measuremetn results: {data_list}")
    await sio.emit("results", [[{"rt60": [.2,.3], "c50": [.2,.3], "c80": [.2,.3], "g": [.2,.3], "d50": [.2,.3]}]], to=lobby.lobby_id)
    await sio.close_room(lobby.lobby_id)
    lobbies.pop(lobby.lobby_id)
    measurement_queues.pop(lobby.lobby_id)
    measurement_tasks.pop(lobby.lobby_id)
    logger.info(f"Lobby {lobby.lobby_id} ended measurement successfully")
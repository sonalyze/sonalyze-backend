import asyncio

from socketio import AsyncServer
from typing import List
from sio.models import Lobby, RecordData

measurement_tasks: dict[str, asyncio.Task] = {}
measurement_queues: dict[str, asyncio.Queue] = {}

async def measurement_controller(sio: AsyncServer, lobby: Lobby):
    await sio.emit("start_measurement", {}, to=lobby.lobby_id)
    measurement_queues[lobby.lobby_id] = asyncio.Queue()

    await asyncio.sleep(1)

    for speaker in lobby.speakers:
        await sio.emit("play_sound", {}, to=speaker.sid)
        await asyncio.sleep(0.5)

    await sio.emit("end_measurement", {}, to=lobby.lobby_id)

    record_data: List[RecordData] = []

    while len(record_data) < len(measurement_queues):
        data = await measurement_queues[lobby.lobby_id].get()
        record_data.append(data)

    # TODO do calculations

    await asyncio.sleep(2)
    await sio.emit("results", {}, lobby.lobby_id)

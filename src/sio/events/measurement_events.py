from pydantic import BaseModel
from socketio import AsyncServer
from typing import cast
import asyncio

from services.measurement_service import measurement_controller, lobbies, measurement_tasks, measurement_queues
from sio.models import SocketSession, RecordData


def register_measurement_events(sio: AsyncServer) -> None:
    @sio.event # type: ignore
    async def start_measurement(sid: str, _: None) -> None:
        session = cast(SocketSession, sio.get_session(sid))
        if not session.isHost:
            return

        if len(lobbies[session.lobby].speakers) == 0:
            await sio.emit("start_measurement_fail", {"reason": "Not enough speakers!"})
        elif len(lobbies[session.lobby].microphones) == 0:
            await sio.emit("start_measurement_fail", {"reason": "Not enough microphones!"})

        task = asyncio.create_task(measurement_controller(sio, lobby=lobbies[session.lobby]))
        measurement_tasks[session.lobby] = task



    class SendRecordEventData(BaseModel):
        recording: str

    @sio.event # type: ignore
    async def send_record_data(sid: str, data: SendRecordEventData) -> None:
        session = cast(SocketSession, sio.get_session(sid))
        await measurement_queues[session.lobby].put(RecordData(sid=sid, recording=data.recording))
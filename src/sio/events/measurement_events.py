from pydantic import BaseModel
from socketio import AsyncServer
from typing import cast
import asyncio

from services.measurement_service import measurement_controller
from sio.models import SocketSession, lobbies


def register_measurement_events(sio: AsyncServer) -> None:
    @sio.event # type: ignore
    def start_measurement(sid: str, data: None) -> None:
        session = cast(SocketSession, sio.get_session(sid))
        if not session.isHost:
            return

        if len(lobbies[session.lobby].speakers) == 0:
            sio.emit("start_measurement_fail", {"reason": "Not enough speakers!"})
        elif len(lobbies[session.lobby].microphones) == 0:
            sio.emit("start_measurement_fail", {"reason": "Not enough speakers!"})

        asyncio.create_task(measurement_controller())






    class SendRecordEventData(BaseModel):
        recording: str

    @sio.event # type: ignore
    def send_record_data(sid: str, data: SendRecordEventData) -> None:
        pass
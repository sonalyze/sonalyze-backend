import logging

import socketio

from services.measurement_service import measurement_tasks, lobbies, measurement_queues
from .events.lobby_events import register_lobby_events
from .events.measurement_events import register_measurement_events
from typing import cast

from .models import SocketSession

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, static_files=None)

logger = logging.getLogger('sio')

@sio.event # type: ignore
async def connect(sid, environ) -> None:
    logger.warning(f"Connected {sid}")

@sio.event # type: ignore
async def disconnect(sid, reason) -> None:
    logger.warning(f"Disconnected {sid}")
    session = cast(SocketSession, await sio.get_session(sid))
    if hasattr(session, 'lobby'):
        if session.lobby in measurement_tasks.keys():
            measurement_tasks[session.lobby].cancel()
            measurement_tasks.pop(session.lobby)

            await sio.emit("cancel_measurement", {"reason": "A client has disconnected"
            }, to=session.lobby)
            lobbies.pop(session.lobby)
            measurement_queues.pop(session.lobby)
            await sio.close_room(session.lobby)

        elif session.lobby in lobbies:
            lobby = lobbies[session.lobby]
            lobby.microphones = list(filter(lambda m: m.sid != sid, lobby.microphones))
            lobby.speakers = list(filter(lambda s: s.sid != sid, lobby.speakers))

            if session.isHost:
                await sio.emit("cancel_measurement", {"reason": "The host has disconnected"
                                                      }, to=session.lobby)
                await sio.close_room(session.lobby)

            mics = list(map(lambda m: m.index, lobby.microphones))
            speakers = list(map(lambda s: s.index, lobby.speakers))

            await sio.emit("device_choices", {
                "microphones": mics,
                "speakers": speakers,
            }, to=lobby.lobby_id)

register_lobby_events(sio)
register_measurement_events(sio)

sio_app = app

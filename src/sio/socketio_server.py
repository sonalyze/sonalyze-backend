import asyncio

import socketio

from services.measurement_service import measurement_tasks, lobbies, measurement_queues
from .events.lobby_events import register_lobby_events
from .events.measurement_events import register_measurement_events
from typing import Dict, cast

from .models import Lobby, RecordData, SocketSession

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, static_files=None)


@sio.event # type: ignore
def connect(sid, environ) -> None:
    print('Client connected:', sid)

@sio.event # type: ignore
async def disconnect(sid) -> None:
    print('Client disconnected:', sid)
    session = cast(SocketSession, sio.get_session(sid))
    if session and session.lobby:
        if measurement_tasks[session.lobby]:
            measurement_tasks[session.lobby].cancel()
            measurement_tasks.pop(session.lobby)

            await sio.emit("cancel_measurement", {"reason": "A client has disconnected"
            }, to=session.lobby)
            lobbies.pop(session.lobby)
            measurement_queues.pop(session.lobby)

        else:
            lobby = lobbies[session.lobby]
            lobby.microphones = list(filter(lambda m: m.sid != sid, lobby.microphones))
            lobby.speakers = list(filter(lambda s: s.sid != sid, lobby.speakers))

            mics = list(map(lambda m: m.index, lobby.microphones))
            speakers = list(map(lambda s: s.index, lobby.speakers))

            await sio.emit("device_choices", {
                "microphones": mics,
                "speakers": speakers,
            }, to=lobby.lobby_id)

@sio.event # type: ignore
def message(sid, data) -> None:
    print('Message from {}: {}'.format(sid, data))
    sio.send(sid, 'Message received: {}'.format(data))

register_lobby_events(sio)
register_measurement_events(sio)

sio_app = app

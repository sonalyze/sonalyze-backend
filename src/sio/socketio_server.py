import logging

import socketio
from bson import ObjectId

from services.measurement_service import measurement_tasks, lobbies, measurement_queues, id_map
from .events.lobby_events import register_lobby_events
from .events.measurement_events import register_measurement_events
from typing import cast

from .models import SocketSession

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, static_files=None)

logger = logging.getLogger("uvicorn.info")

@sio.event # type: ignore
async def connect(sid, environ, auth) -> None:
    if not auth:
        logger.info(f"Refused {sid} because of missing user_id")
        await sio.disconnect(sid)
        return

    token = auth["token"]
    if not ObjectId.is_valid(token):
        logger.info(f"Refused {sid} because of invalid user_id")
        await sio.disconnect(sid)
        return
    id_map[sid] = token
    logger.info(f"Connected {sid} with user_id {token}")

@sio.event # type: ignore
async def disconnect(sid, reason) -> None:
    logger.info(f"Disconnected {sid}")
    session = cast(SocketSession, await sio.get_session(sid))
    if sid in id_map:
        del id_map[sid]

    if hasattr(session, 'lobby'):
        if session.lobby in measurement_tasks.keys():
            measurement_tasks[session.lobby].cancel()
            measurement_tasks.pop(session.lobby)

            await sio.emit("cancel_measurement", {"reason": "A client has disconnected"
            }, to=session.lobby)
            lobbies.pop(session.lobby)
            measurement_queues.pop(session.lobby)
            await sio.close_room(session.lobby)
            logger.info(f"Interrupted measurement of lobby {session.lobby} because {sid} disconnected")

        elif session.lobby in lobbies:
            lobby = lobbies[session.lobby]
            lobby.microphones = list(filter(lambda m: m.sid != sid, lobby.microphones))
            lobby.speakers = list(filter(lambda s: s.sid != sid, lobby.speakers))

            if session.isHost:
                await sio.emit("cancel_measurement", {"reason": "The host has disconnected"
                                                      }, to=session.lobby)
                await sio.close_room(session.lobby)
                lobbies.pop(session.lobby)
                logger.info(f"Host {sid} disconnected from lobby {session.lobby}, lobby closed")

            mics = list(map(lambda m: m.index, lobby.microphones))
            speakers = list(map(lambda s: s.index, lobby.speakers))
            logger.info(f"Client {sid} disconnected from lobby {session.lobby}")

            await sio.emit("device_choices", {
                "microphones": mics,
                "speakers": speakers,
            }, to=lobby.lobby_id)

register_lobby_events(sio)
register_measurement_events(sio)

sio_app = app

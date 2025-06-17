import logging
import uuid

from pydantic import BaseModel, ValidationError
from socketio import AsyncServer
from typing import cast

from services.measurement_service import lobbies, measurement_tasks
from sio.models import Lobby, LobbyClient, SocketSession

logger = logging.getLogger("uvicorn.info")

def register_lobby_events(sio: AsyncServer) -> None:

    @sio.event # type: ignore
    async def create_lobby(sid: str, _: None) -> None:
        lobby_id = str(uuid.uuid4())
        client = LobbyClient(sid=sid, index=0)
        lobbies[lobby_id] = Lobby(host=sid, lobby_id=lobby_id, microphones=[client], speakers=[])
        await sio.save_session(sid, SocketSession(lobby=lobby_id, isHost=True))
        await sio.enter_room(sid, lobby_id)
        await sio.emit("create_lobby_res", {"lobbyId": lobby_id}, to=lobby_id)
        logger.info(f"Created lobby {lobby_id} from {sid}")

    class JoinEventData(BaseModel):
        lobbyId: str

    @sio.event # type: ignore
    async def join_lobby(sid: str, data: JoinEventData) -> None:

        try:
            data = JoinEventData.model_validate(data)
        except ValidationError as e:
            logger.error(e)
            return

        if not data.lobbyId in lobbies:
            await sio.emit("join_lobby_fail", {"reason": "Lobby not found"} ,to=sid)
            return

        if data.lobbyId in measurement_tasks:
            await sio.emit("join_lobby_fail", {"reason": "Lobby already running measurement"}, to=sid)
            return

        await sio.save_session(sid, SocketSession(lobby=data.lobbyId, isHost=False))
        await sio.enter_room(sid, data.lobbyId)
        if len(lobbies[data.lobbyId].speakers) < len(lobbies[data.lobbyId].microphones):
            index = len(lobbies[data.lobbyId].speakers)
            client = LobbyClient(sid=sid, index=index)
            lobbies[data.lobbyId].speakers.append(client)
            await sio.emit("join_lobby_success", {
                "deviceType": "speaker",
                "index": index
            },  to=sid)
        else:
            index = len(lobbies[data.lobbyId].microphones)
            client = LobbyClient(sid=sid, index=index)
            lobbies[data.lobbyId].microphones.append(client)
            await sio.emit("join_lobby_success", {
                "deviceType": "microphone",
                "index": index,
            }, to=sid)

        mics = list(map(lambda m: m.index, lobbies[data.lobbyId].microphones))
        speakers = list(map(lambda s: s.index, lobbies[data.lobbyId].speakers))
        logger.info(f"Client {sid} joined lobby {data.lobbyId}")

        await sio.emit("device_choices", {
            "microphones": mics,
            "speakers": speakers,
        }, to=data.lobbyId)



    class ChoseDeviceTypeEventData(BaseModel):
        device: str
        index: int

    @sio.event # type: ignore
    async def chose_device_type(sid: str, data: ChoseDeviceTypeEventData) -> None:
        try:
            data = ChoseDeviceTypeEventData.model_validate(data)
        except ValidationError as e:
            logger.error(e)
            return

        session = cast(SocketSession, await sio.get_session(sid))

        if not hasattr(session, "lobby"):
            return

        if session.lobby in measurement_tasks:
            await sio.emit("cancel_measurement", {"reason": "Lobby already running measurement"}, to=sid)
            return

        lobby = lobbies[session.lobby]
        lobby.microphones = list(filter(lambda m: m.sid != sid, lobby.microphones))
        lobby.speakers = list(filter(lambda s: s.sid != sid, lobby.speakers))

        if data.device == "speaker":
            lobby.speakers.append(LobbyClient(sid=sid, index=data.index))
        else:
            lobby.microphones.append(LobbyClient(sid=sid, index=data.index))

        mics = list(map(lambda m: m.index, lobby.microphones))
        speakers = list(map(lambda s: s.index, lobby.speakers))

        await sio.emit("device_choices", {
            "microphones": mics,
            "speakers": speakers,
        }, to=lobby.lobby_id)




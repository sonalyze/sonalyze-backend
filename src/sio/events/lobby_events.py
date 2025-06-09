import uuid

from pydantic import BaseModel
from socketio import AsyncServer
from typing import Dict, List, cast

from services.measurement_service import lobbies
from sio.models import Lobby, LobbyClient, SocketSession


def register_lobby_events(sio: AsyncServer) -> None:

    @sio.event # type: ignore
    async def create_lobby(sid: str, _: None) -> None:
        lobby_id = str(uuid.uuid4())
        client = LobbyClient(sid=sid, index=0)
        lobbies[lobby_id] = Lobby(host=sid, lobby_id=lobby_id, microphones=[client], speakers=[])
        await sio.save_session(sid, SocketSession(lobby=lobby_id, isHost=True))
        await sio.enter_room(sid, lobby_id)
        await sio.emit("create_lobby_res", {"lobbyId": lobby_id}, to=lobby_id)

    class JoinEventData(BaseModel):
        lobby_id: str

    @sio.event # type: ignore
    async def join_lobby(sid: str, data: JoinEventData) -> None:
        if not data.lobby_id in lobbies:
            await sio.emit("join_lobby_fail", {"reason": "Lobby not found"} ,to=sid)

        await sio.save_session(sid, SocketSession(lobby=data.lobby_id, isHost=False))
        if len(lobbies[data.lobby_id].speakers) < len(lobbies[data.lobby_id].microphones):
            index = len(lobbies[data.lobby_id].speakers)
            client = LobbyClient(sid=sid, index=index)
            lobbies[data.lobby_id].speakers.append(client)
            await sio.emit("join_lobby_success", {
                "deviceType": "speaker",
                "index": index
            },  to=sid)
        else:
            index = len(lobbies[data.lobby_id].microphones)
            client = LobbyClient(sid=sid, index=index)
            lobbies[data.lobby_id].microphones.append(client)
            await sio.emit("join_lobby_success", {
                "deviceType": "microphone",
                "index": index,
            }, to=sid)

        mics = list(map(lambda m: m.index, lobbies[data.lobby_id].microphones))
        speakers = list(map(lambda s: s.index, lobbies[data.lobby_id].speakers))

        await sio.emit("device_choices", {
            "microphones": mics,
            "speakers": speakers,
        }, to=data.lobby_id)



    class ChoseDeviceTypeEventData(BaseModel):
        device: str
        index: int

    @sio.event # type: ignore
    async def chose_device_type(sid: str, data: ChoseDeviceTypeEventData) -> None:
        session = cast(SocketSession, sio.get_session(sid))
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




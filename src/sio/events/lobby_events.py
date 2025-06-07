import uuid

from pydantic import BaseModel
from socketio import AsyncServer
from typing import Dict, List, Iterable


def register_lobby_events(sio: AsyncServer) -> None:

    class LobbyClient(BaseModel):
        sid: str
        index: int

    class Lobby(BaseModel):
        host: str
        lobby_id: str
        microphones: List[LobbyClient]
        speakers: List[LobbyClient]

    class SocketSession(BaseModel):
        lobby: str
        isHost: bool

    lobbys: Dict[str, Lobby] = {}

    @sio.event # type: ignore
    def create_lobby(sid: str, data: None) -> None:
        lobby_id = str(uuid.uuid4())
        client = LobbyClient(sid=sid, index=0)
        lobbys[lobby_id] = Lobby(host=sid, lobby_id=lobby_id, microphones=[client], speakers=[])
        sio.save_session(sid, SocketSession(lobby=lobby_id, isHost=True))
        sio.enter_room(sid, lobby_id)
        sio.emit("create_lobby_res", {"lobbyId": lobby_id}, to=lobby_id)

    class JoinEventData(BaseModel):
        lobby_id: str

    @sio.event # type: ignore
    def join_lobby(sid: str, data: JoinEventData) -> None:
        if not data.lobby_id in lobbys:
            sio.emit("join_lobby_fail", {"reason": "Lobby not found"} ,to=sid)

        sio.save_session(sid, SocketSession(lobby=data.lobby_id, isHost=False))
        if len(lobbys[data.lobby_id].speakers) < len(lobbys[data.lobby_id].microphones):
            index = len(lobbys[data.lobby_id].speakers)
            client = LobbyClient(sid=sid, index=index)
            lobbys[data.lobby_id].speakers.append(client)
            sio.emit("join_lobby_success", {
                "deviceType": "speaker",
                "index": index,
                "microphoneCount": len(lobbys[data.lobby_id].microphones),
                "speakerCount": len(lobbys[data.lobby_id].speakers),},  to=sid)
        else:
            index = len(lobbys[data.lobby_id].microphones)
            client = LobbyClient(sid=sid, index=index)
            lobbys[data.lobby_id].microphones.append(client)
            sio.emit("join_lobby_success", {
                "deviceType": "microphone",
                "index": index,
                "microphoneCount": len(lobbys[data.lobby_id].microphones),
                "speakerCount": len(lobbys[data.lobby_id].speakers), }, to=sid)

        sio.emit("user_joined_lobby", {
            "microphoneCount": len(lobbys[data.lobby_id].microphones),
            "speakerCount": len(lobbys[data.lobby_id].speakers)}, to=data.lobby_id)



    class ChoseDeviceTypeEventData(BaseModel):
        device: str
        index: int

    @sio.event # type: ignore
    def chose_device_type(sid: str, data: ChoseDeviceTypeEventData) -> None:
        pass



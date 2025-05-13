from pydantic import BaseModel
from socketio import AsyncServer


def register_lobby_events(sio: AsyncServer) -> None:
    @sio.event # type: ignore
    def create_lobby(sid: str, data: None) -> None:
        pass

    class JoinEventData(BaseModel):
        lobbyId: str

    @sio.event # type: ignore
    def join_lobby(sid: str, data: JoinEventData) -> None:
        pass

    class ChoseDeviceTypeEventData(BaseModel):
        device: str
        index: int

    @sio.event # type: ignore
    def chose_device_type(sid: str, data: ChoseDeviceTypeEventData) -> None:
        pass





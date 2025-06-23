from pydantic import BaseModel
from typing import List, Dict


class LobbyClient(BaseModel):
    sid: str
    index: int


class Lobby(BaseModel):
    host: str
    lobby_id: str
    microphones: List[LobbyClient]
    speakers: List[LobbyClient]
    repetitions: int
    delay: float
    distances: dict[int, dict[int, float]]


class SocketSession(BaseModel):
    lobby: str
    isHost: bool

class RecordData(BaseModel):
    sid: str
    recording: str
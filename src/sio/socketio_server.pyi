# socketio.pyi
import asyncio
from typing import TypeVar, Callable, ParamSpec, Any, Optional, Dict

from sio.models import Lobby, RecordData

P = ParamSpec("P")
T = TypeVar("T")

class AsyncServer:
    def on(self, event: str) -> Callable[[Callable[P, T]], Callable[P, T]]: ...
    def event(self, fn: Callable[P, T]) -> Callable[P, T]: ...
    def emit(self, event: str, data: Any, room: Optional[str] = ...) -> None: ...

sio_app: Any

lobbies: Dict[str, Lobby]
measurement_tasks: dict[str, asyncio.Task]
measurement_queues: dict[str, asyncio.Queue[RecordData]]
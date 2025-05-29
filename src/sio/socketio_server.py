import socketio
from .events.lobby_events import register_lobby_events
from .events.measurement_events import register_measurement_events

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, static_files=None)

@sio.event # type: ignore
def connect(sid, environ) -> None:
    print('Client connected:', sid)

@sio.event # type: ignore
def disconnect(sid) -> None:
    print('Client disconnected:', sid)

@sio.event # type: ignore
def message(sid, data) -> None:
    print('Message from {}: {}'.format(sid, data))
    sio.send(sid, 'Message received: {}'.format(data))

register_lobby_events(sio)
register_measurement_events(sio)

sio_app = app

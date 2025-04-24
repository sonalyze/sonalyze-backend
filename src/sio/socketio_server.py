import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, static_files=None)

@sio.event
def connect(sid, environ) -> None:
    print('Client connected:', sid)

@sio.event
def disconnect(sid) -> None:
    print('Client disconnected:', sid)

@sio.event
def message(sid, data) -> None:
    print('Message from {}: {}'.format(sid, data))
    sio.send(sid, 'Message received: {}'.format(data))

sio_app = app

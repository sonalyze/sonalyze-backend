import socketio

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, static_files=None)

@sio.event
def connect(sid, environ):
    print('Client connected:', sid)

@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)

@sio.event
def message(sid, data):
    print('Message from {}: {}'.format(sid, data))
    sio.send(sid, 'Message received: {}'.format(data))

sio_app = app

from fastapi import FastAPI
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from sio.socketio_server import sio_app

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://aal.todo",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", sio_app)

app.include_router(api_router.router, prefix="/api", tags=["api"])
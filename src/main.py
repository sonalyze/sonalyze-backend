from fastapi import FastAPI
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from sio.socketio_server import sio_app
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

origins = [
    "http://localhost:8081",        # ✅ dein echtes Frontend
    "http://127.0.0.1:8081",        # ✅ alternative Adresse
    "http://localhost:3000",        # optional
    "http://127.0.0.1:3000",        # optional
    "https://aal.todo",             # optional
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
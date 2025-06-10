import logging

from fastapi import FastAPI
from api import router as api_router
from fastapi.middleware.cors import CORSMiddleware

from sio.socketio_server import sio_app
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="Sonalyze API",
    description="This is the API for Sonalyze.",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

origins = [
    "http://localhost:8081",
    "https://sonalyze.de",
    "https://dev.sonalyze.de",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/socket.io", sio_app)

app.include_router(api_router.router)

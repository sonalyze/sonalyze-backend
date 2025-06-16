import logging
import base64
from pydantic import BaseModel, ValidationError
from socketio import AsyncServer
from typing import cast
import asyncio

from services.measurement_service import measurement_controller, lobbies, measurement_tasks, measurement_queues
from sio.models import SocketSession, RecordData

logger = logging.getLogger("uvicorn.info")

def register_measurement_events(sio: AsyncServer) -> None:
    @sio.event # type: ignore
    async def start_measurement(sid: str, _: None) -> None:
        session = cast(SocketSession, await sio.get_session(sid))
        if not hasattr(session, "isHost") or not session.isHost or session.lobby in measurement_tasks.keys():
            return

        mic_indices = {c.index for c in lobbies[session.lobby].microphones}
        speaker_indices = {c.index for c in lobbies[session.lobby].speakers}

        if not set(mic_indices) == (set(range(len(mic_indices)))) or not set(speaker_indices) == (set(range(len(speaker_indices)))):
            await sio.emit("start_measurement_fail", {"reason": "Some indices are not filled."})
            return

        if len(lobbies[session.lobby].speakers) == 0:
            await sio.emit("start_measurement_fail", {"reason": "Not enough speakers!"})
            return
        elif len(lobbies[session.lobby].microphones) == 0:
            await sio.emit("start_measurement_fail", {"reason": "Not enough microphones!"})
            return

        task = asyncio.create_task(measurement_controller(sio, lobby=lobbies[session.lobby]))
        measurement_tasks[session.lobby] = task
        logger.info(f"Started measurement for lobby {session.lobby}")



    class SendRecordEventData(BaseModel):
        recording: str

    @sio.event # type: ignore
    async def send_record_data(sid: str, data: SendRecordEventData) -> None:
        try:
            data = SendRecordEventData.model_validate(data)
        except ValidationError as e:
            logger.error(e)
            return
        logger.info(f"Recording Data recieved from {sid}")
        recording_length = len(data.recording)
        logger.info(f"Received audio data: {recording_length} characters")
        sample_prefix = data.recording[:20]
        sample_suffix = data.recording[-20:] if recording_length > 20 else ""
        logger.info(f"Data sample: {sample_prefix}...{sample_suffix}")

               # Verify it's valid base64
        try:
            # Attempt to decode to validate base64 format
            decoded_sample = base64.b64decode(data.recording)
            logger.info(f"Base64 format is valid {decoded_sample[:20]}...{decoded_sample[-20:] if len(decoded_sample) > 20 else ''}")
        except Exception as e:
            logger.error(f"Invalid base64 format: {str(e)}")

        session = cast(SocketSession, await sio.get_session(sid))
        await measurement_queues[session.lobby].put(RecordData(sid=sid, recording=data.recording))
        logger.info(f"Microphone data from {sid} arrived for lobby {session.lobby}")
import asyncio
import logging

import numpy as np
import base64
import io
import soundfile as sf
from bson import ObjectId

from scipy.fft import fft, ifft
from scipy.signal import sosfilt, butter, chirp
from scipy.stats import linregress

from typing import Any
from numpy.typing import NDArray

from database.engine import DataContext
from database.schemas.measurement_db import MeasurementDbModel
from models import AcousticParameters
from socketio import AsyncServer
from typing import List, Dict

from services.analysis_service import analyze_acoustic_parameters, create_in, decode_audio_data
from sio.models import Lobby, RecordData

lobbies: Dict[str, Lobby] = {}
measurement_tasks: dict[str, asyncio.Task] = {} # type: ignore
measurement_queues: dict[str, asyncio.Queue[RecordData]] = {}
id_map: dict[str, str] = {} # maps sid to user_id

logger = logging.getLogger("uvicorn.info")

async def measurement_controller(sio: AsyncServer, lobby: Lobby, ctx: DataContext) -> None:
    await sio.emit("start_measurement", {}, to=lobby.lobby_id)
    measurement_queues[lobby.lobby_id] = asyncio.Queue()
    await asyncio.sleep(4)
    data_list: List[List[RecordData]] = []

    for i in range(lobby.repetitions):
        logger.info(f"measurement cycle {i} for lobby {lobby.lobby_id} started")
        for mic in lobby.microphones:
            await sio.emit("start_recording", {}, to=mic.sid)

        await asyncio.sleep(1)
        for speaker in lobby.speakers:
            await sio.emit("play_sound", {}, to=speaker.sid)
            await asyncio.sleep(6)

        for mic in lobby.microphones:
            await sio.emit("end_recording", {}, to=mic.sid)

        record_data: List[RecordData] = []

        logger.info(f"Lobby {lobby.lobby_id} waiting for recorded data...")
        while len(record_data) < len(lobby.microphones):
            data = await measurement_queues[lobby.lobby_id].get()

            record_data.append(data)

        logger.info(f"Lobby {lobby.lobby_id} received recorded data: {len(record_data)}")
        data_list.append(record_data)
        if i < (lobby.repetitions - 1):
            await asyncio.sleep(lobby.delay)

    await sio.emit("end_measurement", {}, to=lobby.lobby_id)
    recorded_signals_cycles : List[List[NDArray[np.floating]]] = []
    for cycle in data_list:
        recorded_signals : List[NDArray[np.floating]] = []
        for record in cycle:
            audio_data, sample_rate = decode_audio_data(record.recording)
            recorded_signals.append(audio_data)
        recorded_signals_cycles.append(recorded_signals)
    
    # Temporary
    sweep_signal = create_in(48000)

    results = analyze_acoustic_parameters(sweep_signal, recorded_signals_cycles, sample_rate)

    await asyncio.sleep(2)
    logger.info(f"Lobby {lobby.lobby_id} measurement results")

    measurement = MeasurementDbModel(
        values=results,
        ownerToken=lobby.microphones[0].user_id,
        name="Measurement",
    )

    try:
        serializable = [
            [param.model_dump() for param in cycle]
            for cycle in results
        ]
        await sio.emit("results", {"results": serializable, "id": str(measurement.id), "name": measurement.name}, to=lobby.lobby_id)
    except Exception as e:
        logger.error(e)

    measurement = MeasurementDbModel(
        values=results,
        ownerToken=lobby.microphones[0].user_id,
        name="Measurement",
    )

    await ctx.measurements.save(measurement)

    for mic in lobby.microphones:
        user = await ctx.users.find_one_by_id(ObjectId(mic.user_id))
        if user is None:
            logger.info(f"User {mic.user_id} not found")
        else:
            user.measurements.append(str(measurement.id))
            await ctx.users.save(user)


    for speaker in lobby.speakers:
        user = await ctx.users.find_one_by_id(ObjectId(speaker.user_id))
        if user is None:
            logger.info(f"User {speaker.user_id} not found")
        else:
            user.measurements.append(str(measurement.id))
            await ctx.users.save(user)


    await sio.close_room(lobby.lobby_id)
    lobbies.pop(lobby.lobby_id)
    measurement_queues.pop(lobby.lobby_id)
    measurement_tasks.pop(lobby.lobby_id)
    logger.info(f"Lobby {lobby.lobby_id} ended measurement successfully")
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
    try:
        serializable = [
            [param.model_dump() for param in cycle]
            for cycle in results
        ]
        await sio.emit("results", {"results": serializable}, to=lobby.lobby_id)
    except Exception as e:
        logger.error(e)
    else:
        logger.info("emit results")


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
            logger.info("append measurement")
            await ctx.users.save(user)
            logger.info("saved user")


    for speaker in lobby.speakers:
        logger.info("add db speaker")
        user = await ctx.users.find_one_by_id(ObjectId(speaker.user_id))
        if user is None:
            logger.info(f"User {speaker.user_id} not found")
        else:
            user.measurements.append(str(measurement.id))
            logger.info("append measurement")
            await ctx.users.save(user)
            logger.info("saved user")


    await sio.close_room(lobby.lobby_id)
    lobbies.pop(lobby.lobby_id)
    measurement_queues.pop(lobby.lobby_id)
    measurement_tasks.pop(lobby.lobby_id)
    logger.info(f"Lobby {lobby.lobby_id} ended measurement successfully")

def create_in(sample_rate: int) -> Any:
    """Creates logarithmitc sine sweep"""
    duration = 5.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    return chirp(t, f0=20, f1=20000, t1=duration, method="logarithmic")

def decode_audio_data(recording_base64: str) -> tuple[NDArray[np.floating], int]:
    """Decode base64 audio data to numpy array"""
    audio_bytes = base64.b64decode(recording_base64)
    audio_buffer = io.BytesIO(audio_bytes)
    audio_data, sample_rate = sf.read(audio_buffer)
    
    if audio_data.ndim > 1:
        audio_data = np.mean(audio_data, axis=1)
    
    return audio_data, sample_rate

def calculate_transfer_function(in_t: NDArray[np.floating], out_t: NDArray[np.floating]) -> Any:
    """Calculates transferfunction from sine sweep and recorded sine sweep"""
    min_len = min(len(in_t), len(out_t))
    in_t = in_t[:min_len]
    out_t = out_t[:min_len]
    
    in_f = fft(in_t)
    out_f = fft(out_t)
    
    tf = out_f / in_f

    return tf

def extract_impulse_response(tf: NDArray[np.floating]) -> NDArray[np.floating] | Any:
    """Applies inverse fft to transfer function to get impulse response. Finds peaks at the end of ir and rolls them to the front"""
    ir = np.real(ifft(tf))
    
    threshold = 0.00005 * np.max(np.abs(ir))
    
    for i in range(len(ir) - 1, 0, -1):
        if np.abs(ir[i]) > threshold:
            end_idx = i
            break
    else:
        peak = np.argmax(np.abs(ir))
        return ir[peak:]

    found_low = False
    for i in range(end_idx - 1, 0, -1):
        if np.abs(ir[i]) <= threshold:
            found_low = True
        elif found_low and np.abs(ir[i]) > threshold:
            start_idx = i
            break
    else:
        start_idx = 0

    roll_amount = -start_idx
    
    ir_rotated = np.roll(ir, roll_amount)
    
    return ir_rotated

def get_octave_band_filters(fs: int) -> tuple[NDArray[np.floating], list[NDArray[np.floating]]]:
    """Get bands from center frequencies from 1/3 octave and calculates bandpassfilter that will be applied later"""
    center_freqs = np.array([
        100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
        1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000
    ])
    
    center_freqs = center_freqs[center_freqs < fs/2]
    
    filters = []
    
    for fc in center_freqs:
        f1 = fc / (2**(1/6))
        f2 = fc * (2**(1/6))
        
        sos = butter(4, [f1, f2], btype='band', fs=fs, output='sos')
        filters.append(sos)
    
    return center_freqs, filters

def calculate_energy_decay(ir_filtered: NDArray[np.floating], fs: int) -> tuple[NDArray[np.floating], NDArray[np.floating], dict[str, int]]:
    """Calculates energy decay from ir and returns indices where the energy drops below -5db -10db -25db -35db """
    ir_squared = ir_filtered**2
    energy_decay = np.cumsum(ir_squared[::-1])[::-1]
    energy_decay_db = 10 * np.log10(energy_decay / energy_decay[0] + 1e-12)
    time_axis = np.arange(len(ir_filtered)) / fs
    
    indices = {
        'idx_5db': int(np.argmax(energy_decay_db <= -5)),
        'idx_10db': int(np.argmax(energy_decay_db <= -10)),
        'idx_25db': int(np.argmax(energy_decay_db <= -25)),
        'idx_35db': int(np.argmax(energy_decay_db <= -35))
    }
    
    return energy_decay_db, time_axis, indices

def calculate_rt60(ir_filtered: NDArray[np.floating], fs: int) -> Any | float:
    """Calculates rt60 extrapolated from either rt30 or rt20 depending on what is available"""
    energy_decay_db, time_axis, indices = calculate_energy_decay(ir_filtered, fs)
    
    if indices['idx_35db'] > indices['idx_5db'] and energy_decay_db[indices['idx_35db']] <= -35:
        time_range = time_axis[indices['idx_5db']:indices['idx_35db']+1]
        energy_range = energy_decay_db[indices['idx_5db']:indices['idx_35db']+1]
        
        if len(time_range) > 2:
            slope, _, _, _, _ = linregress(time_range, energy_range)
            if slope < 0:
                rt30 = -30 / slope
                return rt30 * 2
    
    if indices['idx_25db'] > indices['idx_5db'] and energy_decay_db[indices['idx_25db']] <= -25:
        time_range = time_axis[indices['idx_5db']:indices['idx_25db']+1]
        energy_range = energy_decay_db[indices['idx_5db']:indices['idx_25db']+1]
        
        if len(time_range) > 2:
            slope, _, _, _, _ = linregress(time_range, energy_range)
            if slope < 0:
                rt20 = -20 / slope
                return rt20 * 3
    
    return np.nan

def calculate_c50(ir_filtered: NDArray[np.floating], fs: int) -> Any | float:
    """Calculates C50 clarity parameter. Used for speach clarity"""
    ir_squared = ir_filtered**2
    idx_50ms = min(int(0.05 * fs), len(ir_squared) - 1)
    
    if idx_50ms < len(ir_squared):
        early_energy_50 = np.sum(ir_squared[:idx_50ms])
        late_energy_50 = np.sum(ir_squared[idx_50ms:])
        
        if late_energy_50 > 0:
            return 10 * np.log10(early_energy_50 / late_energy_50)
    
    return np.nan

def calculate_c80(ir_filtered: NDArray[np.floating], fs: int) -> Any | float:
    """Calculates C50 clarity parameter. Used for music clarity"""
    ir_squared = ir_filtered**2
    idx_80ms = min(int(0.08 * fs), len(ir_squared) - 1)
    
    if idx_80ms < len(ir_squared):
        early_energy_80 = np.sum(ir_squared[:idx_80ms])
        late_energy_80 = np.sum(ir_squared[idx_80ms:])
        
        if late_energy_80 > 0:
            return 10 * np.log10(early_energy_80 / late_energy_80)
    
    return np.nan

def calculate_d50(ir_filtered: NDArray[np.floating], fs: int) -> Any | float:
    """Calculates definition d50"""
    ir_squared = ir_filtered**2
    idx_50ms = min(int(0.05 * fs), len(ir_squared) - 1)
    total_energy = np.sum(ir_squared)
    
    if idx_50ms < len(ir_squared) and total_energy > 0:
        early_energy_50 = np.sum(ir_squared[:idx_50ms])
        return (early_energy_50 / total_energy) * 100
    
    return np.nan

def calculate_g_strength(ir_filtered: NDArray[np.floating], ir_total_energy: float, num_bands: int) -> Any | float:
    """Calculates strength g"""
    ir_squared = ir_filtered**2
    total_energy = np.sum(ir_squared)
    
    if total_energy > 0 and ir_total_energy > 0:
        reference_energy = ir_total_energy / num_bands
        return 10 * np.log10(total_energy / reference_energy)
    
    return np.nan

def calculate_acoustic_parameters(ir: NDArray[np.floating], fs: int, center_freqs: NDArray[np.floating], filters: list[NDArray[np.floating]]) -> AcousticParameters:
    """Applies bandpass filter to ir and collects all parameters for ever 1/3 octave band"""
    rt60_values = []
    c50_values = []
    c80_values = []
    g_values = []
    d50_values = []
    
    ir_total_energy = np.sum(ir**2)
    num_bands = len(center_freqs)
    
    for filter in filters:
        ir_filtered = sosfilt(filter, ir)
        
        rt60 = calculate_rt60(ir_filtered, fs)
        c50 = calculate_c50(ir_filtered, fs)
        c80 = calculate_c80(ir_filtered, fs)
        d50 = calculate_d50(ir_filtered, fs)
        g = calculate_g_strength(ir_filtered, ir_total_energy, num_bands)
        
        rt60_values.append(rt60)
        c50_values.append(c50)
        c80_values.append(c80)
        d50_values.append(d50)
        g_values.append(g)

    return AcousticParameters(
        rt60=rt60_values,
        c50=c50_values,
        c80=c80_values,
        g=g_values,
        d50=d50_values,
        ir=ir.tolist()
    )

def analyze_acoustic_parameters(sweep_signal: NDArray[np.floating], recorded_signals_cycles: list[list[NDArray[np.floating]]], sample_rate: int) -> list[list[AcousticParameters]]:
    """Returns results for every mic speaker configuration"""
    results = []
    
    center_freqs, filters = get_octave_band_filters(sample_rate)
    for recorded_cycle in recorded_signals_cycles:
        results_cycle = []
        for recorded_signal in recorded_cycle:
            tf = calculate_transfer_function(sweep_signal, recorded_signal)
            
            ir = extract_impulse_response(tf)
            
            mic_results = calculate_acoustic_parameters(ir, sample_rate, center_freqs, filters)
            
            results_cycle.append(mic_results)
        results.append(results_cycle)
    return results
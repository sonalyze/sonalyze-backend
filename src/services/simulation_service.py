from api.models.room_scene import RestRoomScene
from api.models.simulation import Simulation
from database.engine import DataContext
import pyroomacoustics as pra
import numpy as np
import logging
from services import get_material
from services.analysis_service import get_octave_band_filters, calculate_acoustic_parameters

logger = logging.getLogger("uvicorn.info")

async def simulate_room(
    room_scene: RestRoomScene, db: DataContext
) -> Simulation | None:
    # Materialien für alle Wände laden
    materials = {}
    for wall in ["east", "west", "north", "south", "ceiling", "floor"]:
        material_name = getattr(room_scene.materials, wall)
        material_data = await get_material.get_material_absorption(material_name, db)
        materials[wall] = pra.Material(
            energy_absorption={
                "coeffs": material_data.coeffs,
                "center_freqs": material_data.center_freqs,
            }
        )

    room_dim = [
        room_scene.dimensions.width,
        room_scene.dimensions.depth,
        room_scene.dimensions.height,
    ]  # Breite, Tiefe, Höhe
    sample_rate = 48000
    room = pra.ShoeBox(
        room_dim, fs=sample_rate, materials=materials, max_order=10
    )  # Standardabsorption mit genauen Materialien ersetzen

    for speaker in room_scene.speakers:
        source_pos = [speaker.x, speaker.y, speaker.z]
        room.add_source(source_pos)

    mic_positions = np.array(
        [
            [m.x for m in room_scene.microphones],
            [m.y for m in room_scene.microphones],
            [m.z for m in room_scene.microphones],
        ]
    )

    room.add_microphone_array(pra.MicrophoneArray(mic_positions, fs=sample_rate))

    room.compute_rir()
    if room.rir is None:
        raise RuntimeError(
            "Raum konnte nicht simmuliert werden – eventuell ist das Setup fehlerhaft."
        )
    results = []
    center_freqs, filters = get_octave_band_filters(sample_rate)
    for mic_index, mic_rirs in enumerate(room.rir):
        results_mic = []
        for source_index, rir in enumerate(mic_rirs):
            mic_results = calculate_acoustic_parameters(rir, sample_rate, center_freqs, filters)
            results_mic.append(mic_results)
        results.append(results_mic)
            # rir ist Impulsantwort die weiterverarbeitet werden muss
            # Verarbeiten der Impulsantwort einfügen

    return Simulation(roomId=room_scene.roomId,values=results)

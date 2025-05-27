from api.models.room_scene import RestRoomScene
from api.models.simulation import Simulation
import pyroomacoustics as pra
import numpy as np


def simulate_room(room_scene: RestRoomScene) -> Simulation | None:
    room_dim = [
        room_scene.dimensions.width,
        room_scene.dimensions.depth,
        room_scene.dimensions.height,
    ]  # Breite, Tiefe, Höhe

    room = pra.ShoeBox(
        room_dim, fs=16000, absorption=0.3, max_order=10
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

    room.add_microphone_array(pra.MicrophoneArray(mic_positions, fs=16000))

    room.compute_rir()
    if room.rir is None:
        raise RuntimeError(
            "Raum konnte nicht simmuliert werden – eventuell ist das Setup fehlerhaft."
        )
    for mic_index, mic_rirs in enumerate(room.rir):
        for source_index, rir in enumerate(mic_rirs):
            print(rir)
            # rir ist Impulsantwort die weiterverarbeitet werden muss
            # Verarbeiten der Impulsantwort einfügen
    return None

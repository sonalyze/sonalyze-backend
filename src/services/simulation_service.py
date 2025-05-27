from api.models.room_scene import RestRoomScene
from api.models.simulation import Simulation
import pyroomacoustics as pra


def simulate_room(room_scene: RestRoomScene) -> Simulation | None:
    room_dim = [
        room_scene.dimensions.width,
        room_scene.dimensions.depth,
        room_scene.dimensions.height,
    ]  # Breite, Tiefe, Höhe
    room = pra.ShoeBox(
        room_dim, fs=16000, absorption=0.3, max_order=10
    )  # Standardabsorption mit genauen Materialien ersetzen
    room_scene.speakers[0].x

    source_location = [
        room_scene.speakers[0].x,
        room_scene.speakers[0].y,
        room_scene.speakers[0].z,
    ]
    room.add_source(source_location)

    room_scene.microphones[0].x
    mic_location = [
        room_scene.microphones[0].x,
        room_scene.microphones[0].y,
        room_scene.microphones[0].z,
    ]
    room.add_microphone(mic_location)

    room.compute_rir()
    if room.rir is None:
        raise RuntimeError(
            "Raum konnte nicht simmuliert werden – eventuell ist das Setup fehlerhaft."
        )
    rir = room.rir[0][0]
    # Verarbeiten der Impulsantwort einfügen
    return None

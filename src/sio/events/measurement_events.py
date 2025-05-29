from pydantic import BaseModel
from socketio import AsyncServer


def register_measurement_events(sio: AsyncServer) -> None:
    @sio.event # type: ignore
    def start_measurement(sid: str, data: None) -> None:
        pass

    class SendRecordEventData(BaseModel):
        recording: str

    @sio.event # type: ignore
    def send_record_data(sid: str, data: SendRecordEventData) -> None:
        pass
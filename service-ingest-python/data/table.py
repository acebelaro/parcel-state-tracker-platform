from abc import ABC, abstractmethod
from typing import Any, NamedTuple


class TelemetryData(NamedTuple):
    parcel_id: str
    device_id: str
    temperature: float
    tilt_x: float
    tilt_y: float
    latitude: float
    longitude: float


class Table(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def save_telemetry(data: Any):
        raise NotImplementedError()

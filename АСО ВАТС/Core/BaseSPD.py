from __future__ import annotations

from abc import abstractmethod, ABC
from dataclasses import dataclass

from .BaseUDPio import BaseUDPSendHandler


@dataclass
class BaseSPD:
    d_id: int
    address: str
    port: str


class BaseSPDMiddleware(BaseUDPSendHandler):
    def __init__(self, context, device, receive_data=False, send_interval=1):
        self.device = device
        super().__init__(context, device.address, device.port, send_interval, receive_data, False)

    def _get_data_to_send(self):
        return self.prepare_data()

    def _process_message(self, message):
        return self.process_response(message)

    @abstractmethod
    def prepare_data(self):
        raise NotImplementedError("Subclasses must implement this method")

    @abstractmethod
    def process_response(self, message):
        raise NotImplementedError("Subclasses must implement this method")


class BaseSPDSet(ABC):
    def __init__(self, context):
        self.context = context
        self.devices = []

    def gather_devices(self, *devs):
        for device in devs:
            self.devices.append(device)

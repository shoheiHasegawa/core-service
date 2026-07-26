from abc import ABC, abstractmethod

from domain.mobile_vault.packet import Packet


class PacketReceiver(ABC):
    @abstractmethod
    def fetch_unprocessed_packets(self) -> list[Packet]:
        pass

    @abstractmethod
    def get_packet(self, packet_id: str) -> Packet | None:
        pass

    @abstractmethod
    def delete_packet(self, packet: Packet) -> None:
        pass

    @abstractmethod
    def get_image_path(self, image_filename: str) -> str | None:
        pass

    @abstractmethod
    def delete_image(self, image_filename: str) -> None:
        pass

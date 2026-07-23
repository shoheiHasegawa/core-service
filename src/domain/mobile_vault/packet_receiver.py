from abc import ABC, abstractmethod

from domain.mobile_vault.packet import Packet


class PacketReceiver(ABC):
    @abstractmethod
    def fetch_unprocessed_packets(self) -> list[Packet]:
        pass

    @abstractmethod
    def delete_packet(self, packet: Packet) -> None:
        pass

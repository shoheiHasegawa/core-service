import uuid
from dataclasses import dataclass


@dataclass
class Packet:
    packet_id: str
    content: str
    images: list[str]

    @classmethod
    def create(cls, content: str, images: list[str]) -> "Packet":
        return cls(packet_id=str(uuid.uuid4()), content=content, images=images)

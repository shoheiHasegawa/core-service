import uuid
from dataclasses import dataclass


@dataclass
class InboxItem:
    item_id: str
    content: str
    images: list[str]

    @classmethod
    def create(cls, content: str, images: list[str]) -> "InboxItem":
        return cls(item_id=str(uuid.uuid4()), content=content, images=images)

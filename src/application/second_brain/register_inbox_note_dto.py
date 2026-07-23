from dataclasses import dataclass, field
from typing import List


@dataclass
class RegisterInboxNoteDto:
    title: str
    content: str
    tags: List[str] = field(default_factory=list)

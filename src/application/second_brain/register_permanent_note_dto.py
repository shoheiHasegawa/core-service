from dataclasses import dataclass, field
from typing import List


@dataclass
class RegisterPermanentNoteDto:
    title: str
    claim: str
    context: str = ""
    connections: str = ""
    tags: List[str] = field(default_factory=list)

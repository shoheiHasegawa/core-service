from dataclasses import dataclass, field
from typing import List


@dataclass
class RegisterSenseMakingNoteDto:
    title: str
    content: str
    source: str = ""
    tags: List[str] = field(default_factory=list)

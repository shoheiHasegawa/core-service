from dataclasses import dataclass
from typing import List


@dataclass
class SecondBrainConfig:
    inbox_dir: str
    sense_making_dir: str
    permanent_notes_dir: str
    attachments_dir: str
    inbox_template_path: str
    sense_making_template_path: str
    permanent_note_template_path: str
    forbidden_patterns: List[str]

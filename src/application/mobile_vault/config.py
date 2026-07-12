from dataclasses import dataclass
from pathlib import Path


@dataclass
class MobileVaultConfig:
    inbox_dir: Path
    attachments_dir: Path
    queue_dir: Path
    dashboard_dir: Path

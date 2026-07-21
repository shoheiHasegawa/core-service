from dataclasses import dataclass


@dataclass
class CalendarConfig:
    calendar_id: str
    credentials_path: str
    api_version: str = "v3"

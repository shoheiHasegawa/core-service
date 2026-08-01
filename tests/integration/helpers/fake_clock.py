from datetime import datetime

from domain.system.clock import Clock


class FakeClock(Clock):
    def __init__(self, current_time: datetime):
        self._current_time = current_time

    def now(self) -> datetime:
        return self._current_time

    def set_time(self, current_time: datetime):
        self._current_time = current_time

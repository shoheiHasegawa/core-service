from datetime import datetime

from domain.system.clock import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now()

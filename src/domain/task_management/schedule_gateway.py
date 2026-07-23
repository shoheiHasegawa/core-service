from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .task import Task


class ScheduleGateway(ABC):
    @abstractmethod
    def sync_schedule(self, target_date: date, tasks: List[Task]) -> None:
        """外部スケジューラ（カレンダー等）へ予定ブロックを同期する"""
        pass

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .task import DailyBriefing, Task


class ITaskRepository(ABC):
    @abstractmethod
    def get_ready_tasks_for_date(self, target_date: date) -> List[Task]:
        """指定日の着手可能タスクを取得する"""
        pass

    @abstractmethod
    def save_tasks(self, tasks: List[Task]) -> None:
        """タスクの状態を保存する"""
        pass


class IScheduleGateway(ABC):
    @abstractmethod
    def sync_schedule(self, target_date: date, tasks: List[Task]) -> None:
        """外部スケジューラ（カレンダー等）へ予定ブロックを同期する"""
        pass


class IBriefingRepository(ABC):
    @abstractmethod
    def save(self, briefing: DailyBriefing) -> None:
        """生成されたDailyBriefing（1日の計画結果）を永続化する"""
        pass

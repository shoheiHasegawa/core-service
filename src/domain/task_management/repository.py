from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING, List

from .task import DailyBriefing, Task

if TYPE_CHECKING:
    from .task import Worklog


class TaskRepository(ABC):
    @abstractmethod
    def get_ready_tasks_for_date(self, target_date: date) -> List[Task]:
        """指定日の着手可能タスクを取得する"""
        pass

    @abstractmethod
    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Task]:
        """指定されたIDのタスクを取得する"""
        pass

    @abstractmethod
    def save_tasks(self, tasks: List[Task]) -> None:
        """タスクの状態を保存する"""
        pass


class ScheduleGateway(ABC):
    @abstractmethod
    def sync_schedule(self, target_date: date, tasks: List[Task]) -> None:
        """外部スケジューラ（カレンダー等）へ予定ブロックを同期する"""
        pass


class BriefingGateway(ABC):
    @abstractmethod
    def save(self, briefing: DailyBriefing) -> None:
        """生成されたDailyBriefing（1日の計画結果）を永続化する"""
        pass

    @abstractmethod
    def get_recent_briefing_contents(self) -> List[str]:
        """直近のダッシュボード（Briefing）のテキスト内容一覧を取得する"""
        pass


class WorklogRepository(ABC):
    @abstractmethod
    def save(self, worklog: "Worklog") -> None:
        """ワークログを保存する"""
        pass

    @abstractmethod
    def find_by_task_and_date(self, task_id: str, target_date: date) -> List["Worklog"]:
        """指定したタスクと日付のワークログを取得する"""
        pass

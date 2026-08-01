from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .task import Task


class TaskRepository(ABC):
    @abstractmethod
    def get_ready_tasks_for_date(self, target_date: date) -> List[Task]:
        """指定日の着手可能タスクを取得する"""
        pass

    @abstractmethod
    def get_uncompleted_past_tasks(self, current_date: date) -> List[Task]:
        """過去の日付にアサインされて未完了のタスクを取得する"""
        pass

    @abstractmethod
    def get_backlog_tasks(self) -> List[Task]:
        """日付未定のバックログタスク(TODO)を取得する"""
        pass

    @abstractmethod
    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Task]:
        """指定されたIDのタスクを取得する"""
        pass

    @abstractmethod
    def save_tasks(self, tasks: List[Task]) -> None:
        """タスクの状態を保存する"""
        pass

    @abstractmethod
    def find_by_id(self, task_id: str) -> "Task | None":
        """指定されたIDの単一タスクを取得する"""
        pass

    @abstractmethod
    def save(self, task: Task) -> None:
        """単一のタスクを保存する"""
        pass

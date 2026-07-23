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
    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Task]:
        """指定されたIDのタスクを取得する"""
        pass

    @abstractmethod
    def save_tasks(self, tasks: List[Task]) -> None:
        """タスクの状態を保存する"""
        pass

from abc import ABC, abstractmethod
from datetime import date
from typing import TYPE_CHECKING, List

from .task import Worklog

if TYPE_CHECKING:
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

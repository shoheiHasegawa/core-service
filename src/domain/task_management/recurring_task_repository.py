from abc import ABC, abstractmethod
from datetime import date
from typing import List

from .recurring_task import RecurringTask


class RecurringTaskRepository(ABC):
    @abstractmethod
    def save(self, recurring_task: RecurringTask) -> None:
        """ルーチンタスクの設定を保存する"""
        pass

    @abstractmethod
    def find_active_by_date(self, target_date: date) -> List[RecurringTask]:
        """指定された日付に有効なルーチンルールを取得する"""
        pass

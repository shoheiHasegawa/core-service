from abc import ABC, abstractmethod
from datetime import date
from typing import List


class CalendarGateway(ABC):
    @abstractmethod
    def fetch_fixed_events(self, target_date: date) -> List[dict]:
        """指定日の固定イベントを外部カレンダーから取得する"""
        pass

    @abstractmethod
    def fetch_all_day_events(self, target_date: date) -> list[str]:
        """指定日の終日イベント（文字列リスト）を外部カレンダーから取得する"""
        pass

    @abstractmethod
    def sync_daily_briefing(self, target_date: date, scheduled_tasks: list) -> None:
        """計算されたスケジュールを外部カレンダーに同期する"""
        pass

from datetime import date
from typing import List

from domain.interfaces.calendar_repository import CalendarRepository


class GoogleCalendarRepository(CalendarRepository):
    def __init__(self, service_account_info: dict = None) -> None:
        self.service_account_info = service_account_info
        # import googleapiclient.discovery  # for future implementation

    def fetch_fixed_events(self, target_date: date) -> List[dict]:
        """Google Calendar APIを利用して指定日の固定イベントを取得する(スタブ)"""
        return []

    def fetch_all_day_events(self, target_date: date) -> list[str]:
        """Google Calendar APIを利用して指定日の終日イベントを取得する(スタブ)"""
        return []

    def sync_daily_briefing(self, target_date: date, scheduled_tasks: list) -> None:
        """Google Calendar APIを利用してスケジュールを同期する(スタブ)"""
        pass

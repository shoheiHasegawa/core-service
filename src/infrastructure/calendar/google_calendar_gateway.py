import datetime
from typing import List

import googleapiclient.discovery
from google.oauth2 import service_account

from domain.interfaces.calendar_gateway import CalendarGateway
from infrastructure.calendar.config import CalendarConfig


class GoogleCalendarGateway(CalendarGateway):
    def __init__(self, config: CalendarConfig) -> None:
        self.config = config

        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.config.credentials_path, scopes=["https://www.googleapis.com/auth/calendar"]
            )
            self.service = googleapiclient.discovery.build("calendar", self.config.api_version, credentials=credentials)
        except Exception:
            self.service = googleapiclient.discovery.build("calendar", self.config.api_version)

    def fetch_fixed_events(self, target_date: datetime.date) -> List[dict]:
        """Google Calendar APIを利用して指定日の固定イベントを取得する"""
        start_time = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
        end_time = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + "Z"

        events_result = (
            self.service.events()
            .list(
                calendarId=self.config.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        return [e for e in events if "dateTime" in e.get("start", {})]

    def fetch_all_day_events(self, target_date: datetime.date) -> list[str]:
        """Google Calendar APIを利用して指定日の終日イベントを取得する"""
        start_time = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
        end_time = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + "Z"

        events_result = (
            self.service.events()
            .list(
                calendarId=self.config.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])
        return [e["summary"] for e in events if "date" in e.get("start", {})]

    def sync_daily_briefing(self, target_date: datetime.date, scheduled_tasks: list) -> None:
        """Google Calendar APIを利用してスケジュールを同期する"""
        start_time = datetime.datetime.combine(target_date, datetime.time.min).isoformat() + "Z"
        end_time = datetime.datetime.combine(target_date, datetime.time.max).isoformat() + "Z"

        events_result = (
            self.service.events()
            .list(
                calendarId=self.config.calendar_id,
                timeMin=start_time,
                timeMax=end_time,
                privateExtendedProperty="source=you_inc",
            )
            .execute()
        )
        existing_events = events_result.get("items", [])

        existing_map = {
            e["extendedProperties"]["private"]["you_inc_task_id"]: e
            for e in existing_events
            if "extendedProperties" in e
            and "private" in e["extendedProperties"]
            and "you_inc_task_id" in e["extendedProperties"]["private"]
        }

        for task in scheduled_tasks:
            task_id = getattr(task, "id", str(task))
            event_body = {
                "summary": getattr(task, "title", "Task"),
                "start": {"date": target_date.isoformat()},
                "end": {"date": target_date.isoformat()},
                "extendedProperties": {"private": {"you_inc_task_id": task_id, "source": "you_inc"}},
            }

            if task_id in existing_map:
                event_id = existing_map[task_id]["id"]
                self.service.events().update(
                    calendarId=self.config.calendar_id, eventId=event_id, body=event_body
                ).execute()
            else:
                self.service.events().insert(calendarId=self.config.calendar_id, body=event_body).execute()

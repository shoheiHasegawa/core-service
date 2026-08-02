import datetime
from dataclasses import dataclass
from typing import List

import googleapiclient.discovery
from google.oauth2 import service_account

from domain.task_management.calendar_gateway import CalendarGateway


@dataclass
class CalendarConfig:
    calendar_id: str
    credentials_path: str
    api_version: str = "v3"


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
        start_time = f"{target_date.isoformat()}T00:00:00+09:00"
        end_time = f"{target_date.isoformat()}T23:59:59+09:00"

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

        scheduled_task_ids = {getattr(t, "id", str(t)) for t in scheduled_tasks}

        # Reconciliation: 余剰イベントの削除
        for task_id, existing_event in existing_map.items():
            if task_id not in scheduled_task_ids:
                self.service.events().delete(
                    calendarId=self.config.calendar_id,
                    eventId=existing_event["id"],
                ).execute()

        for task in scheduled_tasks:
            task_id = getattr(task, "id", str(task))
            start_val = getattr(task, "start_time", None)
            end_val = getattr(task, "end_time", None)

            if start_val and end_val:
                start_iso = start_val.isoformat() if hasattr(start_val, "isoformat") else str(start_val)
                end_iso = end_val.isoformat() if hasattr(end_val, "isoformat") else str(end_val)
                if "+" not in start_iso and not start_iso.endswith("Z"):
                    start_iso += "+09:00"
                if "+" not in end_iso and not end_iso.endswith("Z"):
                    end_iso += "+09:00"

                start_obj = {"dateTime": start_iso, "timeZone": "Asia/Tokyo"}
                end_obj = {"dateTime": end_iso, "timeZone": "Asia/Tokyo"}
            else:
                next_day = target_date + datetime.timedelta(days=1)
                start_obj = {"date": target_date.isoformat()}
                end_obj = {"date": next_day.isoformat()}

            event_body = {
                "summary": getattr(task, "title", "Task"),
                "start": start_obj,
                "end": end_obj,
                "extendedProperties": {"private": {"you_inc_task_id": task_id, "source": "you_inc"}},
            }

            if task_id in existing_map:
                event_id = existing_map[task_id]["id"]
                self.service.events().update(
                    calendarId=self.config.calendar_id, eventId=event_id, body=event_body
                ).execute()
            else:
                self.service.events().insert(calendarId=self.config.calendar_id, body=event_body).execute()

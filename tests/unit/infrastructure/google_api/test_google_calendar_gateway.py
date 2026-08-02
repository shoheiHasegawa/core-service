import datetime
from unittest.mock import patch

from domain.task_management.task import Task, TaskCategory
from infrastructure.google_api.google_calendar_gateway import CalendarConfig, GoogleCalendarGateway


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_fetch_fixed_events_uses_build(mock_build, mock_creds):
    """
    [TM-SYNC-01] GoogleCalendarGateway.fetch_fixed_eventsの検証
    """
    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarGateway(config=config)
    target_date = datetime.date(2026, 7, 21)

    repo.fetch_fixed_events(target_date)

    mock_build.assert_called_once()
    mock_build.return_value.events.assert_called()
    assert mock_build.called


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_fetch_all_day_events_uses_build(mock_build, mock_creds):
    """
    [TM-PLAN-06] GoogleCalendarGateway.fetch_all_day_eventsの検証
    """
    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarGateway(config=config)
    target_date = datetime.date(2026, 7, 21)

    repo.fetch_all_day_events(target_date)

    mock_build.assert_called_once()
    mock_build.return_value.events.assert_called()
    assert mock_build.called


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_sync_daily_briefing_uses_build(mock_build, mock_creds):
    """
    [TM-SYNC-01] GoogleCalendarGateway.sync_daily_briefingの検証
    """
    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarGateway(config=config)
    target_date = datetime.date(2026, 7, 21)

    repo.sync_daily_briefing(target_date, [])

    mock_build.assert_called_once()
    mock_build.return_value.events.assert_called()
    assert mock_build.called


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_sync_daily_briefing_time_blocked_events(mock_build, mock_creds):
    """
    タスクに start_time / end_time が設定されている場合、dateTime を持つイベントとして同期されること
    """
    mock_events = mock_build.return_value.events.return_value
    mock_events.list.return_value.execute.return_value = {"items": []}

    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarGateway(config=config)
    target_date = datetime.date(2026, 8, 3)

    task = Task(
        id="task-123",
        title="Deep Work Task",
        category=TaskCategory.MUST,
        estimated_minutes=120,
        start_time=datetime.datetime(2026, 8, 3, 7, 0, 0),
        end_time=datetime.datetime(2026, 8, 3, 9, 0, 0),
    )

    repo.sync_daily_briefing(target_date, [task])

    mock_events.insert.assert_called_once()
    _, kwargs = mock_events.insert.call_args
    body = kwargs.get("body", {})
    assert "dateTime" in body.get("start", {})
    assert "2026-08-03T07:00:00" in body["start"]["dateTime"]
    assert "dateTime" in body.get("end", {})
    assert "2026-08-03T09:00:00" in body["end"]["dateTime"]
    assert body.get("extendedProperties", {}).get("private", {}).get("you_inc_task_id") == "task-123"
    assert body.get("extendedProperties", {}).get("private", {}).get("source") == "you_inc"


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_sync_daily_briefing_all_day_events_exclusive_end(mock_build, mock_creds):
    """
    タスクの start_time が None の場合、終日予定として同期され、end.date は翌日（排他）となること
    """
    mock_events = mock_build.return_value.events.return_value
    mock_events.list.return_value.execute.return_value = {"items": []}

    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarGateway(config=config)
    target_date = datetime.date(2026, 8, 3)

    task = Task(
        id="task-456",
        title="All Day Task",
        category=TaskCategory.SHOULD,
        estimated_minutes=60,
        start_time=None,
        end_time=None,
    )

    repo.sync_daily_briefing(target_date, [task])

    mock_events.insert.assert_called_once()
    _, kwargs = mock_events.insert.call_args
    body = kwargs.get("body", {})
    assert body.get("start") == {"date": "2026-08-03"}
    assert body.get("end") == {"date": "2026-08-04"}


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_sync_daily_briefing_deletes_obsolete_events(mock_build, mock_creds):
    """
    Reconciliation: カレンダー上に存在するが scheduled_tasks に含まれない you_inc イベントは delete されること
    """
    mock_events = mock_build.return_value.events.return_value
    mock_events.list.return_value.execute.return_value = {
        "items": [
            {
                "id": "event-old-id",
                "summary": "Old Task",
                "extendedProperties": {
                    "private": {
                        "you_inc_task_id": "task-old",
                        "source": "you_inc",
                    }
                },
            }
        ]
    }

    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarGateway(config=config)
    target_date = datetime.date(2026, 8, 3)

    task_new = Task(
        id="task-new",
        title="New Task",
        category=TaskCategory.WANT,
        estimated_minutes=30,
    )

    repo.sync_daily_briefing(target_date, [task_new])

    # task-old should be deleted
    mock_events.delete.assert_called_once_with(
        calendarId="test@example.com",
        eventId="event-old-id",
    )
    # task-new should be inserted
    mock_events.insert.assert_called_once()
    _, kwargs = mock_events.insert.call_args
    body = kwargs.get("body", {})
    assert body.get("extendedProperties", {}).get("private", {}).get("you_inc_task_id") == "task-new"


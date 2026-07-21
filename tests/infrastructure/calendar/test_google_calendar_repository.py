import datetime
from unittest.mock import patch

from infrastructure.calendar.config import CalendarConfig
from infrastructure.calendar.google_calendar_repository import GoogleCalendarRepository


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_fetch_fixed_events_uses_build(mock_build, mock_creds):
    """
    [TM-SYNC-01] GoogleCalendarRepository.fetch_fixed_eventsの検証
    """
    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarRepository(config=config)
    target_date = datetime.date(2026, 7, 21)

    repo.fetch_fixed_events(target_date)

    mock_build.assert_called_once()
    mock_build.return_value.events.assert_called()


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_fetch_all_day_events_uses_build(mock_build, mock_creds):
    """
    [TM-PLAN-06] GoogleCalendarRepository.fetch_all_day_eventsの検証
    """
    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarRepository(config=config)
    target_date = datetime.date(2026, 7, 21)

    repo.fetch_all_day_events(target_date)

    mock_build.assert_called_once()
    mock_build.return_value.events.assert_called()


@patch("google.oauth2.service_account.Credentials.from_service_account_file", autospec=True)
@patch("googleapiclient.discovery.build", autospec=True)
def test_sync_daily_briefing_uses_build(mock_build, mock_creds):
    """
    [TM-SYNC-01] GoogleCalendarRepository.sync_daily_briefingの検証
    """
    config = CalendarConfig(calendar_id="test@example.com", credentials_path="dummy.json")
    repo = GoogleCalendarRepository(config=config)
    target_date = datetime.date(2026, 7, 21)

    repo.sync_daily_briefing(target_date, [])

    mock_build.assert_called_once()
    mock_build.return_value.events.assert_called()

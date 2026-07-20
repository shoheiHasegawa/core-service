from datetime import date
from typing import List

from application.task_management.daily_action_service import DailyActionService

# 以下のimportは現在は存在しないためImportErrorになります（Red状態）
from domain.interfaces.calendar_repository import CalendarRepository
from domain.task_management.task import Task, TaskCategory


class FakeCalendarRepository(CalendarRepository):
    def __init__(self):
        self.fetch_fixed_events_called = 0
        self.sync_daily_briefing_called = 0
        self.last_sync_tasks = []

    def fetch_fixed_events(self, target_date: date) -> List[dict]:
        self.fetch_fixed_events_called += 1
        return []

    def fetch_all_day_events(self, target_date: date) -> List[str]:
        return []

    def sync_daily_briefing(self, target_date: date, scheduled_tasks: list) -> None:
        self.sync_daily_briefing_called += 1
        self.last_sync_tasks = scheduled_tasks


class FakeTaskRepository:
    def get_ready_tasks_for_date(self, target_date):
        return [Task(id="t1", title="Must 1", category=TaskCategory.MUST, estimated_minutes=30)]


class FakeScheduleGateway:
    def sync_schedule(self, target_date, tasks):
        pass


class FakeBriefingRepository:
    def save(self, briefing):
        pass


class FakeWorklogRepository:
    pass


def test_daily_action_service_sync_to_calendar():
    """[TM-SYNC-01] plan_day実行時に同期フラグがTrueなら、計算されたスケジュールがcalendar_repositoryに同期されること"""
    task_repo = FakeTaskRepository()
    fake_calendar_repo = FakeCalendarRepository()

    service = DailyActionService(
        task_repo=task_repo,
        schedule_gateway=FakeScheduleGateway(),
        briefing_repo=FakeBriefingRepository(),
        worklog_repo=FakeWorklogRepository(),
        calendar_repo=fake_calendar_repo
    )

    # 同期フラグを立てて実行
    briefing = service.plan_day(date.today(), sync_to_calendar=True)

    # 同期メソッドが呼ばれたことをアサート
    assert fake_calendar_repo.sync_daily_briefing_called == 1
    assert fake_calendar_repo.last_sync_tasks == briefing.scheduled_tasks

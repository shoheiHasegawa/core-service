import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.task_management.daily_action_service import DailyActionService
from domain.interfaces.calendar_gateway import CalendarGateway
from domain.task_management.repository import BriefingGateway, ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeCalendarGateway(CalendarGateway):
    def __init__(self):
        self.synced_blocks = []
        self.sync_called = False

    def fetch_fixed_events(self, target_date: datetime.date) -> list:
        return []

    def fetch_all_day_events(self, target_date: datetime.date) -> list:
        return []

    def sync_daily_briefing(self, target_date: datetime.date, scheduled_tasks: list) -> None:
        self.sync_called = True
        self.synced_blocks = scheduled_tasks


class FakeScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: datetime.date, tasks: List[Task]) -> None:
        pass


class FakeBriefingGateway(BriefingGateway):
    def save(self, briefing) -> None:
        pass

    def get_recent_briefing_contents(self) -> list[str]:
        return []


def test_calendar_sync_integration_flow(test_context: IntegrationTestContext):
    """
    [TM-SYNC-01]
    SQLite(In-Memory) の TaskRepository と FakeCalendarGateway を結合し、
    DailyActionService が正常にスケジュールを計算し、カレンダー同期までの一連のフローを完了できるかを検証する。
    """
    task_repo = test_context.task_repo
    calendar_gateway = FakeCalendarGateway()
    schedule_gateway = FakeScheduleGateway()
    briefing_gateway = FakeBriefingGateway()
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)

    service = DailyActionService(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        briefing_repo=briefing_gateway,
        worklog_repo=worklog_repo,
        calendar_repo=calendar_gateway,
    )

    target_date = datetime.date(2026, 7, 20)

    # 準備: テスト用のタスク群を作成
    tasks = [
        Task(
            id="task-sync-test",
            title="Sync Integration Task",
            category=TaskCategory.MUST,
            estimated_minutes=60,
            area_id="01_Work",
            target_date=target_date,
        )
    ]
    task_repo.save_tasks(tasks)

    # 実行 (Act)
    briefing = service.plan_day(target_date=target_date, sync_to_calendar=True)

    # 検証 (Assert)
    # スケジュールが計算されたこと
    assert len(briefing.scheduled_tasks) >= 1
    # DBと連携してタスクが読み込まれ、カレンダー同期メソッドまで正常に到達したこと
    assert calendar_gateway.sync_called is True
    assert len(calendar_gateway.synced_blocks) == len(briefing.scheduled_tasks)

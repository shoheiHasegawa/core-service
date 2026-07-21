import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.task_management.daily_action_service import DailyActionService
from domain.interfaces.calendar_repository import CalendarRepository
from domain.task_management.repository import BriefingRepository, ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeCalendarRepository(CalendarRepository):
    def __init__(self, all_day_events=None):
        self.all_day_events = all_day_events or []
        self.synced_tasks = None

    def fetch_fixed_events(self, target_date: datetime.date) -> List[dict]:
        return []

    def fetch_all_day_events(self, target_date: datetime.date) -> List[str]:
        return self.all_day_events

    def sync_daily_briefing(self, target_date: datetime.date, scheduled_tasks: list) -> None:
        self.synced_tasks = scheduled_tasks


class FakeScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: datetime.date, tasks: List[Task]) -> None:
        pass


class FakeBriefingRepository(BriefingRepository):
    def __init__(self):
        self.saved_briefing = None

    def save(self, briefing) -> None:
        self.saved_briefing = briefing


def test_sync_calendar_and_metadata_integration(test_context: IntegrationTestContext):
    """
    [TM-SYNC-01] 正常系: 決定されたスケジュールを外部SoR（カレンダー）に同期する
    [TM-PLAN-06] アーキテクチャ原則: SoR分離と終日予定のメタデータ化
    [TM-SYNC-03] 正常系: DailyBriefingのMarkdown連携 (Mobile Vault同期)
    """
    task_repo = test_context.task_repo
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)
    schedule_gateway = FakeScheduleGateway()
    briefing_repo = FakeBriefingRepository()

    # [TM-PLAN-06] 終日イベントをメタデータとして扱う ("有給"等をフラグとして注入)
    calendar_repo = FakeCalendarRepository(all_day_events=["有給"])

    service = DailyActionService(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        briefing_repo=briefing_repo,
        worklog_repo=worklog_repo,
        calendar_repo=calendar_repo,
    )

    target_date = datetime.date(2026, 7, 21)
    tasks = [
        Task(
            id="task-sync-1",
            title="Sync Task 1",
            category=TaskCategory.MUST,
            estimated_minutes=60,
            target_date=target_date,
        )
    ]
    task_repo.save_tasks(tasks)

    # [TM-SYNC-01] 同期フラグTrueで実行
    briefing = service.plan_day(target_date=target_date, sync_to_calendar=True)

    # Assert (ここでRedになるか検証)
    assert calendar_repo.synced_tasks is not None, "カレンダーへの同期が呼び出されること"
    assert len(calendar_repo.synced_tasks) == len(briefing.scheduled_tasks)
    
    # [TM-SYNC-03] Mobile Vaultへの同期が呼び出されること
    assert briefing_repo.saved_briefing is not None, "BriefingRepositoryが呼び出されること"
    assert briefing_repo.saved_briefing.target_date == target_date

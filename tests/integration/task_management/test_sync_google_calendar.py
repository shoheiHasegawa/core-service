import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.daily_planning.plan_day_usecase import PlanDayUseCase
from domain.task_management.calendar_gateway import CalendarGateway
from domain.task_management.schedule_gateway import ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.sqlalchemy.worklog_repository import SQLAlchemyWorklogRepository


class FakeCalendarGateway(CalendarGateway):
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


def test_sync_calendar_and_metadata_integration(test_context: IntegrationTestContext):
    """
    [TM-SYNC-01] 正常系: 決定されたスケジュールを外部SoR（カレンダー）に同期する
    [TM-PLAN-13] アーキテクチャ原則: SoR分離と終日予定のメタデータ化
    [TM-SYNC-03] 正常系: DailyBriefingのMarkdown連携 (Mobile Vault同期)
    """
    task_repo = test_context.task_repo
    SQLAlchemyWorklogRepository(test_context.session)
    schedule_gateway = FakeScheduleGateway()

    # [TM-PLAN-13] 終日イベントをメタデータとして扱う ("有給"等をフラグとして注入)
    calendar_gateway = FakeCalendarGateway(all_day_events=["有給"])

    service = PlanDayUseCase(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        calendar_repo=calendar_gateway,
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
    briefing = service.execute(target_date=target_date, sync_to_calendar=True)

    # Assert (ここでRedになるか検証)
    assert calendar_gateway.synced_tasks is not None, "カレンダーへの同期が呼び出されること"
    assert len(calendar_gateway.synced_tasks) == len(briefing.scheduled_tasks)

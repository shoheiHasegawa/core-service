import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.daily_planning.plan_day_usecase import PlanDayUseCase
from domain.interfaces.calendar_gateway import CalendarGateway
from domain.task_management.recurring_task import RecurringTask
from domain.task_management.repository import BriefingGateway, ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.recurring_task_repository import SqlRecurringTaskRepository
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: datetime.date, tasks: List[Task]) -> None:
        pass


class FakeBriefingGateway(BriefingGateway):
    def save(self, briefing) -> None:
        pass

    def get_recent_briefing_contents(self) -> list[str]:
        return []


class FakeCalendarGateway(CalendarGateway):
    def __init__(self, events_map=None):
        self.events_map = events_map or {}

    def fetch_fixed_events(self, target_date: datetime.date) -> List[dict]:
        return []

    def sync_daily_briefing(self, target_date: datetime.date, scheduled_tasks: list) -> None:
        pass

    def fetch_all_day_events(self, target_date: datetime.date) -> List[str]:
        return self.events_map.get(target_date, [])


def test_daily_action_service_holiday_context(test_context: IntegrationTestContext):
    """[TM-PLAN-04] PlanDayUseCase.execute の祝日・有給判定と day_context の検証
    Requirement: [TASK-EPIC05-PHASE3]
    """
    task_repo = test_context.task_repo
    schedule_gateway = FakeScheduleGateway()
    briefing_gateway = FakeBriefingGateway()
    SQLAlchemyWorklogRepository(test_context.session)
    recurring_task_repo = SqlRecurringTaskRepository(test_context.session)

    # 2026-07-21 (火) に有給イベントを設定
    calendar_gateway = FakeCalendarGateway(events_map={datetime.date(2026, 7, 21): ["有給休暇", "ゴミの日"]})

    service = PlanDayUseCase(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        briefing_repo=briefing_gateway,
        calendar_repo=calendar_gateway,
        recurring_task_repo=recurring_task_repo,
    )

    # テスト用の RecurringTask をセットアップ (毎日実行される設定にしておく: * * * * *)
    workday_task = RecurringTask(
        id="rt-workday",
        name="Workday Task",
        rule_type="cron",
        cron_schedule="* * * * *",
        start_time="09:00",
        end_time="10:00",
        duration_minutes=60,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
        day_context="WORKDAY",
    )

    any_task = RecurringTask(
        id="rt-any",
        name="Any Task",
        rule_type="cron",
        cron_schedule="* * * * *",
        start_time="05:00",
        end_time="07:00",
        duration_minutes=120,
        category=TaskCategory.SHOULD,
        valid_from=None,
        valid_until=None,
        day_context="ANY",
    )

    recurring_task_repo.save(workday_task)
    recurring_task_repo.save(any_task)
    test_context.session.commit()

    # --- 1. 祝日の判定: 2026-01-01 (木) ---
    date_holiday = datetime.date(2026, 1, 1)
    briefing_1 = service.execute(date_holiday)
    scheduled_task_names_1 = [t.title for t in briefing_1.scheduled_tasks]
    assert "Workday Task" not in scheduled_task_names_1, "祝日なのでWORKDAYタスクはスケジュールされない"
    assert "Any Task" in scheduled_task_names_1, "ANYタスクは常にスケジュールされる"

    # --- 2. 有給休暇の判定: 2026-07-21 (火) ---
    date_pto = datetime.date(2026, 7, 21)
    briefing_2 = service.execute(date_pto)
    scheduled_task_names_2 = [t.title for t in briefing_2.scheduled_tasks]
    assert "Workday Task" not in scheduled_task_names_2, "有休なのでWORKDAYタスクはスケジュールされない"
    assert "Any Task" in scheduled_task_names_2, "ANYタスクは常にスケジュールされる"

    # --- 3. 通常の平日: 2026-07-22 (水) ---
    date_workday = datetime.date(2026, 7, 22)
    briefing_3 = service.execute(date_workday)
    scheduled_task_names_3 = [t.title for t in briefing_3.scheduled_tasks]
    assert "Workday Task" in scheduled_task_names_3, "平日なのでWORKDAYタスクはスケジュールされる"
    assert "Any Task" in scheduled_task_names_3, "ANYタスクは常にスケジュールされる"

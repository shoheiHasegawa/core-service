import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.task_management.daily_action_service import DailyActionService
from domain.task_management.recurring_task import RecurringTask
from domain.task_management.repository import BriefingRepository, ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.recurring_task_repository import SqlRecurringTaskRepository
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: datetime.date, tasks: List[Task]) -> None:
        pass


class FakeBriefingRepository(BriefingRepository):
    def save(self, briefing) -> None:
        pass


def test_daily_action_service_recurring_tasks(test_context: IntegrationTestContext):
    """
    [TM-SYNC-02] 正常系: RecurringTask が絶対枠（固定ブロック）としてスケジュールに自動配置されることを検証する
    """
    task_repo = test_context.task_repo
    schedule_gateway = FakeScheduleGateway()
    briefing_repo = FakeBriefingRepository()
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)
    recurring_task_repo = SqlRecurringTaskRepository(test_context.session)

    # RecurringTasks をセットアップ
    # 月・金 7:00-9:00 の筋トレ (SHOULD)
    muscle_training = RecurringTask(
        id="rt-muscle",
        name="筋トレ",
        rule_type="cron",
        cron_schedule="0 7 * * 1,5",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.SHOULD,
        valid_from=None,
        valid_until=None
    )

    # 平日 5:00-7:00 のDeep Work (MUST)
    deep_work = RecurringTask(
        id="rt-deepwork",
        name="Deep Work",
        rule_type="cron",
        cron_schedule="0 5 * * 1-5",
        start_time="05:00",
        end_time="07:00",
        duration_minutes=120,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None
    )

    recurring_task_repo.save(muscle_training)
    recurring_task_repo.save(deep_work)

    # 依存する普通の流動タスクもいくつか用意
    target_date = datetime.date(2026, 7, 20)  # 月曜日
    normal_task = Task(
        id="task-normal",
        title="Normal Task",
        category=TaskCategory.MUST,
        estimated_minutes=60,
        area_id="01_Work",
        target_date=target_date,
    )
    task_repo.save_tasks([normal_task])

    # サービスを生成（現在は recurring_task_repo を受け付けないためここで TypeError が起きる想定）
    service = DailyActionService(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        briefing_repo=briefing_repo,
        worklog_repo=worklog_repo,
        recurring_task_repo=recurring_task_repo
    )

    # 実行
    briefing = service.plan_day(target_date)

    # 検証
    scheduled_tasks = briefing.scheduled_tasks

    # ScheduledTask または Task としてカレンダーに同期されるリスト内に筋トレとDeepWorkが含まれていること
    scheduled_titles = [getattr(t, "title", getattr(t, "name", "")) for t in scheduled_tasks]

    assert any("筋トレ" in t for t in scheduled_titles), "筋トレの枠がスケジュールに組み込まれていること"
    assert any("Deep Work" in t for t in scheduled_titles), "Deep Workの枠がスケジュールに組み込まれていること"

    # 時間帯が指定通りに配置されていることの検証
    muscle_task = next((t for t in scheduled_tasks if "筋トレ" in getattr(t, "title", getattr(t, "name", ""))), None)
    assert muscle_task is not None
    assert muscle_task.start_time.hour == 7, "筋トレは7:00に開始すること"
    assert muscle_task.start_time.minute == 0, "筋トレは7:00に開始すること"

    deep_work_task = next((t for t in scheduled_tasks if "Deep Work" in getattr(t, "title", getattr(t, "name", ""))), None)
    assert deep_work_task is not None
    assert deep_work_task.start_time.hour == 5, "Deep Workは5:00に開始すること"
    assert deep_work_task.start_time.minute == 0, "Deep Workは5:00に開始すること"

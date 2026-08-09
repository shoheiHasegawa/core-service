import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.daily_planning.plan_day_usecase import PlanDayUseCase
from domain.task_management.calendar_gateway import CalendarGateway
from domain.task_management.recurring_task import RecurringTask
from domain.task_management.schedule_gateway import ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.sqlalchemy.recurring_task_repository import SqlRecurringTaskRepository


class FakeCalendarGateway(CalendarGateway):
    def __init__(self):
        self.synced_tasks = []
        self.call_count = 0

    def fetch_fixed_events(self, target_date: datetime.date) -> List[dict]:
        return []

    def fetch_all_day_events(self, target_date: datetime.date) -> List[str]:
        return []

    def sync_daily_briefing(self, target_date: datetime.date, scheduled_tasks: list) -> None:
        self.call_count += 1
        self.synced_tasks = scheduled_tasks


class FakeScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: datetime.date, tasks: List[Task]) -> None:
        pass


def test_plan_day_idempotency_consecutive_runs(test_context: IntegrationTestContext):
    """
    [TM-PLAN-14] 冪等性: 同一日付に対して plan_day が複数回実行されても、
    タスク・スケジュール・カレンダー同期内容に重複が発生しないこと
    [TM-PLAN-15] 固定時間定期タスク（fixed_time）は定義された時間枠に必ず配置され、再実行によって押し出されないこと
    """
    task_repo = test_context.task_repo
    recurring_task_repo = SqlRecurringTaskRepository(test_context.session)
    calendar_gateway = FakeCalendarGateway()
    schedule_gateway = FakeScheduleGateway()

    # 1. 定期タスク (筋トレ: 07:00-09:00) を登録
    muscle_training = RecurringTask(
        id="rt-muscle",
        name="月金 7:00-9:00 の筋トレ",
        rule_type="cron",
        cron_schedule="0 7 * * 1,5",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.SHOULD,
        valid_from=None,
        valid_until=None,
    )
    recurring_task_repo.save(muscle_training)

    # 2. 通常タスクを1件登録
    target_date = datetime.date(2026, 8, 3)  # 月曜日
    one_off_task = Task(
        id="task-one-off-1",
        title="重要タスク",
        category=TaskCategory.MUST,
        estimated_minutes=60,
        area_id="01_Work",
        target_date=target_date,
    )
    task_repo.save_tasks([one_off_task])

    usecase = PlanDayUseCase(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        calendar_repo=calendar_gateway,
        recurring_task_repo=recurring_task_repo,
    )

    # 1回目の実行
    usecase.execute(target_date, sync_to_calendar=True)

    # 2回目の実行 (日中の再生成・再計画をシミュレート)
    briefing_2 = usecase.execute(target_date, sync_to_calendar=True)

    # 検証1: 2回目の scheduled_tasks に重複がないこと
    task_ids_2 = [t.id for t in briefing_2.scheduled_tasks]
    assert len(task_ids_2) == len(set(task_ids_2)), f"Duplicate task IDs found: {task_ids_2}"

    # 検証2: 筋トレタスクの開始時刻が 07:00 のままであること (夜間にズレていないこと)
    muscle_task = next((t for t in briefing_2.scheduled_tasks if "筋トレ" in t.title), None)
    assert muscle_task is not None
    assert muscle_task.start_time.hour == 7
    assert muscle_task.start_time.minute == 0

    # 検証3: カレンダー同期タスクにも重複がなく、筋トレの開始時刻が正常であること
    synced_ids = [t.id for t in calendar_gateway.synced_tasks]
    assert len(synced_ids) == len(set(synced_ids)), f"Duplicate synced task IDs: {synced_ids}"
    synced_muscle = next((t for t in calendar_gateway.synced_tasks if "筋トレ" in t.title), None)
    assert synced_muscle is not None
    assert synced_muscle.start_time.hour == 7


def test_plan_day_empty_tasks_boundary(test_context: IntegrationTestContext):
    """
    [TM-PLAN-16] 境界値・空データ: タスクが0件の場合でも、活動時間（05:00-20:00）の範囲内で固定定期タスクのみで構成された有効なスケジュールが生成されること
    """
    task_repo = test_context.task_repo
    recurring_task_repo = SqlRecurringTaskRepository(test_context.session)
    calendar_gateway = FakeCalendarGateway()
    schedule_gateway = FakeScheduleGateway()

    # 定期タスク (07:00-09:00) のみを登録、通常タスクは0件
    recurring_task = RecurringTask(
        id="rt-empty-test",
        name="朝のルーティン",
        rule_type="cron",
        cron_schedule="0 7 * * 1-5",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    recurring_task_repo.save(recurring_task)

    target_date = datetime.date(2026, 8, 3)
    usecase = PlanDayUseCase(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        calendar_repo=calendar_gateway,
        recurring_task_repo=recurring_task_repo,
    )

    briefing = usecase.execute(target_date, sync_to_calendar=True)

    assert briefing is not None
    assert len(briefing.scheduled_tasks) >= 1
    routine_task = next((t for t in briefing.scheduled_tasks if "朝のルーティン" in t.title), None)
    assert routine_task is not None
    assert routine_task.start_time.hour == 7


def test_plan_day_domain_invariants_no_overlapping(test_context: IntegrationTestContext):
    """
    [TM-PLAN-17] ドメイン不変条件: 生成されたスケジュール内の全ブロックにおいて、時間帯の不正な重複（Overlap）が絶対に存在しないこと
    """
    task_repo = test_context.task_repo
    recurring_task_repo = SqlRecurringTaskRepository(test_context.session)
    calendar_gateway = FakeCalendarGateway()
    schedule_gateway = FakeScheduleGateway()

    # 複数の定期タスクと通常タスクを混在登録
    rt1 = RecurringTask(
        id="rt-inv-1",
        name="午前ブロック",
        rule_type="cron",
        cron_schedule="0 9 * * 1-5",
        start_time="09:00",
        end_time="12:00",
        duration_minutes=180,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    rt2 = RecurringTask(
        id="rt-inv-2",
        name="午後ブロック",
        rule_type="cron",
        cron_schedule="0 13 * * 1-5",
        start_time="13:00",
        end_time="18:00",
        duration_minutes=300,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    recurring_task_repo.save(rt1)
    recurring_task_repo.save(rt2)

    target_date = datetime.date(2026, 8, 3)
    tasks = [
        Task(id="inv-t1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=45, target_date=target_date),
        Task(id="inv-t2", title="Task 2", category=TaskCategory.SHOULD, estimated_minutes=60, target_date=target_date),
    ]
    task_repo.save_tasks(tasks)

    usecase = PlanDayUseCase(
        task_repo=task_repo,
        schedule_gateway=schedule_gateway,
        calendar_repo=calendar_gateway,
        recurring_task_repo=recurring_task_repo,
    )

    briefing = usecase.execute(target_date, sync_to_calendar=True)

    # 開始時刻・終了時刻が設定されているタスク間で時間重複がないことを検証
    timed_tasks = [
        t for t in briefing.scheduled_tasks if getattr(t, "start_time", None) and getattr(t, "end_time", None)
    ]
    timed_tasks.sort(key=lambda t: t.start_time)

    for i in range(len(timed_tasks) - 1):
        current_t = timed_tasks[i]
        next_t = timed_tasks[i + 1]
        assert current_t.end_time <= next_t.start_time, (
            f"Overlap detected: {current_t.title} ({current_t.start_time}-{current_t.end_time}) "
            f"overlaps with {next_t.title} ({next_t.start_time}-{next_t.end_time})"
        )

from datetime import date

from domain.task_management.recurring_task import RecurringTask
from domain.task_management.task import TaskCategory
from infrastructure.task_management.recurring_task_repository import SqlRecurringTaskRepository


def test_save_and_restore_recurring_task(test_context):
    """[TM-SYNC-02] RecurringTaskを保存し、正しく復元できること"""
    repo = SqlRecurringTaskRepository(test_context.session)

    task = RecurringTask(
        id="rt-001",
        name="Morning Routine",
        rule_type="fixed_time",
        cron_schedule="0 7 * * 1,5",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.MUST,
        valid_from=date(2026, 7, 1),
        valid_until=date(2026, 12, 31)
    )
    repo.save(task)

    test_context.session.commit()
    test_context.session.expire_all()

    active_tasks = repo.find_active_by_date(date(2026, 7, 20))
    assert len(active_tasks) == 1

    restored_task = active_tasks[0]
    assert restored_task.id == "rt-001"
    assert restored_task.name == "Morning Routine"
    assert restored_task.rule_type == "fixed_time"
    assert restored_task.cron_schedule == "0 7 * * 1,5"
    assert restored_task.start_time == "07:00"
    assert restored_task.end_time == "09:00"
    assert restored_task.duration_minutes == 120
    assert restored_task.category == TaskCategory.MUST
    assert restored_task.valid_from == date(2026, 7, 1)
    assert restored_task.valid_until == date(2026, 12, 31)


def test_find_active_by_date(test_context):
    """[TM-SYNC-02] find_active_by_date(date) は、指定した日付が valid_from 〜 valid_until の期間内にある（または Null である）タスクのみを返すこと"""
    repo = SqlRecurringTaskRepository(test_context.session)

    task_active = RecurringTask(
        id="rt-active",
        name="Active Task",
        rule_type="fixed_time",
        cron_schedule="0 7 * * *",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.SHOULD,
        valid_from=date(2026, 7, 1),
        valid_until=date(2026, 7, 31)
    )

    task_expired = RecurringTask(
        id="rt-expired",
        name="Expired Task",
        rule_type="fixed_time",
        cron_schedule="0 7 * * *",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.SHOULD,
        valid_from=date(2026, 1, 1),
        valid_until=date(2026, 6, 30)
    )

    task_always = RecurringTask(
        id="rt-always",
        name="Always Task",
        rule_type="flexible_date",
        cron_schedule="0 12 * * 1",
        start_time=None,
        end_time=None,
        duration_minutes=60,
        category=TaskCategory.SHOULD,
        valid_from=None,
        valid_until=None
    )

    repo.save(task_active)
    repo.save(task_expired)
    repo.save(task_always)

    test_context.session.commit()
    test_context.session.expire_all()

    results = repo.find_active_by_date(date(2026, 7, 20))

    assert len(results) == 2
    result_ids = {t.id for t in results}
    assert "rt-active" in result_ids
    assert "rt-always" in result_ids
    assert "rt-expired" not in result_ids


def test_save_and_restore_recurring_task_with_day_context(test_context):
    """[TM-PLAN-04] [TASK-EPIC05-PHASE1] RecurringTaskのday_contextを保存し、正しく復元できること"""
    repo = SqlRecurringTaskRepository(test_context.session)

    task = RecurringTask(
        id="rt-day-context",
        name="Workday Routine",
        rule_type="fixed_time",
        cron_schedule="0 7 * * 1,5",
        start_time="07:00",
        end_time="09:00",
        duration_minutes=120,
        category=TaskCategory.MUST,
        valid_from=date(2026, 7, 1),
        valid_until=date(2026, 12, 31),
        day_context="WORKDAY"
    )
    repo.save(task)

    test_context.session.commit()
    test_context.session.expire_all()

    active_tasks = repo.find_active_by_date(date(2026, 7, 20))
    restored_task = next((t for t in active_tasks if t.id == "rt-day-context"), None)

    assert restored_task is not None
    assert restored_task.day_context == "WORKDAY"


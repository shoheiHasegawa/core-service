from datetime import date

from domain.task_management.recurring_task import RecurringTask
from domain.task_management.task import TaskCategory, TaskType


def create_recurring_task(day_context="ANY", cron_schedule="* * * * *"):
    return RecurringTask(
        id="test_id",
        name="Test Task",
        rule_type="cron",
        cron_schedule=cron_schedule,
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
        day_context=day_context,
    )


def test_is_scheduled_on_workday_fails_on_holiday():
    """
    [TM-PLAN-04]
    WORKDAY判定: day_context="WORKDAY" かつ is_holiday=True の場合、
    CRONの曜日が一致していても is_scheduled_on は False を返すこと。
    """
    task = create_recurring_task(day_context="WORKDAY", cron_schedule="* * * * 1-5")
    # target_date is a Monday, which matches cron, but it's a holiday
    target_date = date(2026, 7, 20)  # 2026-07-20 is Monday
    assert not task.is_scheduled_on(target_date, is_holiday=True)


def test_is_scheduled_on_holiday_fails_on_workday():
    """
    [TM-PLAN-04]
    HOLIDAY判定: day_context="HOLIDAY" かつ is_holiday=False (稼働日) の場合、
    CRONの曜日が一致していても is_scheduled_on は False を返すこと。
    """
    task = create_recurring_task(day_context="HOLIDAY", cron_schedule="* * * * 1-5")
    # target_date is a Monday, which matches cron, but it's a workday
    target_date = date(2026, 7, 13)  # 2026-07-13 is Monday
    assert not task.is_scheduled_on(target_date, is_holiday=False)


def test_is_scheduled_on_any_returns_true_regardless_of_holiday():
    """
    [TM-PLAN-04]
    ANY判定: day_context="ANY" の場合、is_holiday の値に関わらず、
    CRONの曜日が一致していれば is_scheduled_on は True を返すこと。
    """
    task = create_recurring_task(day_context="ANY", cron_schedule="* * * * 1-5")
    target_date = date(2026, 7, 20)  # 2026-07-20 is Monday
    assert task.is_scheduled_on(target_date, is_holiday=True)

    target_date_workday = date(2026, 7, 13)  # 2026-07-13 is Monday
    assert task.is_scheduled_on(target_date_workday, is_holiday=False)


def test_to_task_creates_task_with_recurring_type():
    """
    RecurringTask.to_task(target_date) で生成される Task の task_type が TaskType.RECURRING であることを検証する。
    """
    rt = RecurringTask(
        id="rt-001",
        name="Daily Standup",
        rule_type="cron",
        cron_schedule="0 9 * * 1-5",
        start_time="09:00",
        end_time="09:30",
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
        day_context="WORKDAY",
    )
    target_date = date(2026, 8, 3)
    task = rt.to_task(target_date)

    assert task.id == "rt-001_20260803"
    assert task.title == "Daily Standup"
    assert task.category == TaskCategory.MUST
    assert task.task_type == TaskType.RECURRING
    assert task.estimated_minutes == 30
    assert task.area_id == "00_Recurring"
    assert task.target_date == target_date
    assert task.start_time is not None
    assert task.start_time.hour == 9 and task.start_time.minute == 0
    assert task.end_time is not None
    assert task.end_time.hour == 9 and task.end_time.minute == 30

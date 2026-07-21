from datetime import date

from domain.task_management.recurring_task import RecurringTask
from domain.task_management.task import TaskCategory


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
    [TM-PLAN-04] [TASK-EPIC05-PHASE2]
    WORKDAY判定: day_context="WORKDAY" かつ is_holiday=True の場合、
    CRONの曜日が一致していても is_scheduled_on は False を返すこと。
    """
    task = create_recurring_task(day_context="WORKDAY", cron_schedule="* * * * 1-5")
    # target_date is a Monday, which matches cron, but it's a holiday
    target_date = date(2026, 7, 20)  # 2026-07-20 is Monday
    assert not task.is_scheduled_on(target_date, is_holiday=True)


def test_is_scheduled_on_holiday_fails_on_workday():
    """
    [TM-PLAN-04] [TASK-EPIC05-PHASE2]
    HOLIDAY判定: day_context="HOLIDAY" かつ is_holiday=False (稼働日) の場合、
    CRONの曜日が一致していても is_scheduled_on は False を返すこと。
    """
    task = create_recurring_task(day_context="HOLIDAY", cron_schedule="* * * * 1-5")
    # target_date is a Monday, which matches cron, but it's a workday
    target_date = date(2026, 7, 13)  # 2026-07-13 is Monday
    assert not task.is_scheduled_on(target_date, is_holiday=False)


def test_is_scheduled_on_any_returns_true_regardless_of_holiday():
    """
    [TM-PLAN-04] [TASK-EPIC05-PHASE2]
    ANY判定: day_context="ANY" の場合、is_holiday の値に関わらず、
    CRONの曜日が一致していれば is_scheduled_on は True を返すこと。
    """
    task = create_recurring_task(day_context="ANY", cron_schedule="* * * * 1-5")
    target_date = date(2026, 7, 20)  # 2026-07-20 is Monday
    assert task.is_scheduled_on(target_date, is_holiday=True)

    target_date_workday = date(2026, 7, 13)  # 2026-07-13 is Monday
    assert task.is_scheduled_on(target_date_workday, is_holiday=False)

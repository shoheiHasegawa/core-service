from datetime import date

from domain.task_management.recurring_task import RecurringTask
from domain.task_management.task import TaskCategory


def test_recurring_task_cron_parsing_months():
    """
    [TM-PLAN-01] Months parsing logic test
    """
    rt = RecurringTask(
        id="rt1",
        name="Test",
        rule_type="cron",
        cron_schedule="0 0 * 1-3,5 *",
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    # January
    assert rt.is_scheduled_on(date(2026, 1, 15)) is True
    # February
    assert rt.is_scheduled_on(date(2026, 2, 10)) is True
    # March
    assert rt.is_scheduled_on(date(2026, 3, 5)) is True
    # April
    assert rt.is_scheduled_on(date(2026, 4, 20)) is False
    # May
    assert rt.is_scheduled_on(date(2026, 5, 2)) is True


def test_recurring_task_cron_parsing_dom():
    """
    [TM-PLAN-01] DOM parsing logic test
    """
    rt = RecurringTask(
        id="rt2",
        name="Test",
        rule_type="cron",
        cron_schedule="0 0 1-5,15 * *",
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    assert rt.is_scheduled_on(date(2026, 1, 3)) is True
    assert rt.is_scheduled_on(date(2026, 1, 15)) is True
    assert rt.is_scheduled_on(date(2026, 1, 10)) is False


def test_recurring_task_cron_parsing_dow():
    """
    [TM-PLAN-01] DOW parsing logic test
    """
    rt = RecurringTask(
        id="rt3",
        name="Test",
        rule_type="cron",
        cron_schedule="0 0 * * 1-3,5",
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    # 2026-08-03 is a Monday (1)
    assert rt.is_scheduled_on(date(2026, 8, 3)) is True
    # 2026-08-04 is a Tuesday (2)
    assert rt.is_scheduled_on(date(2026, 8, 4)) is True
    # 2026-08-06 is a Thursday (4)
    assert rt.is_scheduled_on(date(2026, 8, 6)) is False
    # 2026-08-07 is a Friday (5)
    assert rt.is_scheduled_on(date(2026, 8, 7)) is True


def test_recurring_task_cron_parsing_dom_and_dow_or():
    """
    [TM-PLAN-01] DOM and DOW OR condition parsing logic test
    """
    rt = RecurringTask(
        id="rt4",
        name="Test",
        rule_type="cron",
        cron_schedule="0 0 1 * 1",
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    # 2026-08-01 is a Saturday, DOM is 1 (True), DOW is 6 (False) -> Should be True because OR
    assert rt.is_scheduled_on(date(2026, 8, 1)) is True
    # 2026-08-03 is Monday, DOM is 3 (False), DOW is 1 (True) -> Should be True
    assert rt.is_scheduled_on(date(2026, 8, 3)) is True
    # 2026-08-04 is Tuesday, DOM is 4 (False), DOW is 2 (False) -> False
    assert rt.is_scheduled_on(date(2026, 8, 4)) is False


def test_recurring_task_invalid_cron():
    """
    [TM-PLAN-01] Invalid cron string parsing logic test
    """
    rt = RecurringTask(
        id="rt_invalid",
        name="Test",
        rule_type="cron",
        cron_schedule="invalid cron",
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    assert rt.is_scheduled_on(date(2026, 1, 1)) is False


def test_recurring_task_empty_cron():
    """
    [TM-PLAN-01] Empty cron string parsing logic test
    """
    rt = RecurringTask(
        id="rt_empty",
        name="Test",
        rule_type="cron",
        cron_schedule="",
        start_time=None,
        end_time=None,
        duration_minutes=30,
        category=TaskCategory.MUST,
        valid_from=None,
        valid_until=None,
    )
    assert rt.is_scheduled_on(date(2026, 1, 1)) is False

from datetime import date

from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType


def test_task_model_extension():
    """[TM-PLAN-01]"""
    """
    [TM-PLAN-07-01] TaskType Enum exists, and Task has task_type, area_id, cumulative_minutes with default values.
    """

    assert hasattr(TaskType, "ONE_OFF")
    assert hasattr(TaskType, "ROUTINE")
    assert hasattr(TaskType, "RECURRING")

    task = Task(
        id="t1",
        title="Test Task",
        category=TaskCategory.MUST,
        estimated_minutes=30,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 18),
        dependencies=[],
    )

    assert task.task_type == TaskType.ONE_OFF
    assert task.area_id == "00_Unknown"
    assert task.cumulative_minutes == 0


def test_task_reference_id_extension():
    """[TM-PLAN-01]"""
    """
    [TM-PLAN-07-03] Task has reference_id with default value None.
    """
    task = Task(
        id="t2",
        title="Test Task Reference ID",
        category=TaskCategory.MUST,
        estimated_minutes=30,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 18),
        dependencies=[],
    )

    assert hasattr(task, "reference_id")
    assert task.reference_id is None


def test_worklog_enums():
    """[TM-PLAN-01] WorklogエンティティのEnumが正しく生成・保持されることを確認する"""
    import datetime

    from domain.task_management.task import TaskCategory, TaskType, Worklog

    target_date = datetime.date(2026, 7, 30)
    wl = Worklog(
        id="wl-1",
        task_id="t1",
        minutes=30,
        is_completed=True,
        target_date=target_date,
        memo="メモテスト",
        area_id="00_Dev",
        category=TaskCategory.WANT,
        task_type=TaskType.ROUTINE,
    )
    assert wl.category == TaskCategory.WANT
    assert wl.task_type == TaskType.ROUTINE
    assert wl.memo == "メモテスト"


def test_record_work():
    """[TM-PLAN-01] TaskからWorklogを記録（生成）できることを確認する"""
    task = Task(id="t1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=30, area_id="00_Dev")

    # Test setting to IN_PROGRESS
    task.record_work(15, False, "test memo")
    assert task.actual_minutes == 15
    assert task.status == TaskStatus.IN_PROGRESS
    assert task.last_memo == "test memo"

    # Test completing
    task.record_work(15, True, "done")
    assert task.actual_minutes == 30
    assert task.status == TaskStatus.COMPLETED
    assert task.last_memo == "done"

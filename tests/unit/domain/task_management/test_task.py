from datetime import date

from domain.task_management.task import Task, TaskCategory, TaskStatus


def test_task_model_extension():
    """[TASK-01]"""
    """
    [TASK-07-01] TaskType Enum exists, and Task has task_type, area_id, cumulative_minutes with default values.
    """
    from domain.task_management.task import TaskType

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


def test_energy_level_removed():
    """[TASK-01]"""
    """
    [TASK-07-02] EnergyLevel Enum is deleted, and Task does not use energy_level.
    """
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

    assert not hasattr(task, "energy_level")


def test_task_reference_id_extension():
    """[TASK-01]"""
    """
    [TASK-07-03] Task has reference_id with default value None.
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

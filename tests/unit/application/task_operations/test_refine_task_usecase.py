from datetime import date
from unittest.mock import MagicMock

import pytest

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType
from domain.task_management.task_repository import TaskRepository


def test_refine_task_happy_path():
    """[TO-REF-01]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    initial_task = Task(id="task_id_123", title="Old Title", category=TaskCategory.MUST, estimated_minutes=30)
    repo.get_tasks_by_ids.return_value = [initial_task]

    refined = usecase.execute(
        task_id="task_id_123",
        title="New Title",
        estimated_minutes=60,
        category=TaskCategory.WANT,
        deadline=date(2026, 9, 1),
        status=TaskStatus.IN_PROGRESS,
        task_type=TaskType.ROUTINE,
        area_id="03_Work",
        energy_level="High",
        dependencies=["dep_task_1"],
        last_memo="Updated Memo",
    )

    assert refined.id == "task_id_123"
    assert refined.title == "New Title"
    assert refined.estimated_minutes == 60
    assert refined.category == TaskCategory.WANT
    assert refined.deadline == date(2026, 9, 1)
    assert refined.status == TaskStatus.IN_PROGRESS
    assert refined.task_type == TaskType.ROUTINE
    assert refined.area_id == "03_Work"
    assert refined.energy_level == "High"
    assert refined.dependencies == ["dep_task_1"]
    assert refined.last_memo == "Updated Memo"
    repo.save_tasks.assert_called_once_with([initial_task])


def test_refine_task_idempotency():
    """[TO-REF-02]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    task = Task(id="task_id_123", title="Old Title", category=TaskCategory.MUST, estimated_minutes=30)
    repo.get_tasks_by_ids.return_value = [task]

    usecase.execute(task_id="task_id_123", title="Same Title", estimated_minutes=45)
    usecase.execute(task_id="task_id_123", title="Same Title", estimated_minutes=45)

    assert task.title == "Same Title"
    assert task.estimated_minutes == 45


def test_refine_task_boundary_validation():
    """[TO-REF-03]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    task = Task(id="task_id_123", title="Old Title", category=TaskCategory.MUST, estimated_minutes=30)
    repo.get_tasks_by_ids.return_value = [task]

    with pytest.raises(ValueError, match="Title must not be empty") as exc_info1:
        usecase.execute(task_id="task_id_123", title="")
    assert "Title must not be empty" in str(exc_info1.value)

    with pytest.raises(ValueError, match="Title must not be empty") as exc_info2:
        usecase.execute(task_id="task_id_123", title="   ")
    assert "Title must not be empty" in str(exc_info2.value)

    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info3:
        usecase.execute(task_id="task_id_123", estimated_minutes=0)
    assert "Estimated minutes must be positive" in str(exc_info3.value)

    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info4:
        usecase.execute(task_id="task_id_123", estimated_minutes=-10)
    assert "Estimated minutes must be positive" in str(exc_info4.value)


def test_refine_task_reconciliation_self_dependency():
    """[TO-REF-04]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    task = Task(id="task_id_123", title="Old Title", category=TaskCategory.MUST, estimated_minutes=30)
    repo.get_tasks_by_ids.return_value = [task]

    with pytest.raises(ValueError, match="cannot depend on itself") as exc_info:
        usecase.execute(task_id="task_id_123", dependencies=["task_id_123"])
    assert "cannot depend on itself" in str(exc_info.value)


def test_refine_task_fault_tolerance_not_found():
    """[TO-REF-05]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    repo.get_tasks_by_ids.return_value = []

    with pytest.raises(ValueError, match="not found") as exc_info:
        usecase.execute("task_id_456")
    assert "not found" in str(exc_info.value)

from unittest.mock import MagicMock

import pytest

from application.task_operations.register_task_usecase import RegisterTaskUseCase
from domain.system.uuid_generator import UUIDGenerator
from domain.task_management.task import TaskCategory, TaskType
from domain.task_management.task_repository import TaskRepository


def test_register_task_happy_path():
    """[TO-REG-01]"""
    repo = MagicMock(spec=TaskRepository)
    uuid_gen = MagicMock(spec=UUIDGenerator)
    uuid_gen.generate.return_value = "fixed-uuid-123"

    usecase = RegisterTaskUseCase(repo, uuid_gen)
    task = usecase.execute(
        title="Test Title",
        category=TaskCategory.MUST,
        estimated_minutes=45,
        reference_id="REF-1",
        task_type=TaskType.ROUTINE,
        area_id="02_Health",
        last_memo="My Memo",
    )

    assert task.id == "fixed-uuid-123"
    assert task.title == "Test Title"
    assert task.category == TaskCategory.MUST
    assert task.estimated_minutes == 45
    assert task.reference_id == "REF-1"
    assert task.task_type == TaskType.ROUTINE
    assert task.area_id == "02_Health"
    assert task.last_memo == "My Memo"
    repo.save_tasks.assert_called_once_with([task])


def test_register_task_boundary_empty_title():
    """[TO-REG-02]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RegisterTaskUseCase(repo)

    with pytest.raises(ValueError, match="Title must not be empty") as exc_info1:
        usecase.execute(title="")
    assert "Title must not be empty" in str(exc_info1.value)

    with pytest.raises(ValueError, match="Title must not be empty") as exc_info2:
        usecase.execute(title="   ")
    assert "Title must not be empty" in str(exc_info2.value)


def test_register_task_boundary_invalid_minutes():
    """[TO-REG-03]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RegisterTaskUseCase(repo)

    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info1:
        usecase.execute(title="Valid", estimated_minutes=0)
    assert "Estimated minutes must be positive" in str(exc_info1.value)

    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info2:
        usecase.execute(title="Valid", estimated_minutes=-10)
    assert "Estimated minutes must be positive" in str(exc_info2.value)

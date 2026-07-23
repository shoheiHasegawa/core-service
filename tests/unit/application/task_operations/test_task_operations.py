from unittest.mock import MagicMock

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task, TaskCategory


def test_register_task():
    """[TO-REG-01]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RegisterTaskUseCase(repo)
    task = usecase.execute("Test Title", "Test Description")
    assert task.title == "Test Title"
    repo.save_tasks.assert_called_once_with([task])


def test_refine_task():
    """[TO-REF-01]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    task = Task(id="task_id_123", title="Mock", category=TaskCategory.MUST, estimated_minutes=30)
    repo.get_tasks_by_ids.return_value = [task]

    refined = usecase.execute("task_id_123")
    assert refined.id == "task_id_123"
    repo.save_tasks.assert_called_once_with([task])


def test_refine_task_not_found():
    """[TO-REF-02]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RefineTaskUseCase(repo)
    repo.get_tasks_by_ids.return_value = []

    refined = usecase.execute("task_id_456")
    assert refined is None

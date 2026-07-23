from unittest.mock import MagicMock

from application.task_operations.register_task_usecase import RegisterTaskUseCase
from domain.task_management.task_repository import TaskRepository


def test_register_task():
    """[TO-REG-01]"""
    repo = MagicMock(spec=TaskRepository)
    usecase = RegisterTaskUseCase(repo)
    task = usecase.execute("Test Title", "Test Description")
    assert task.title == "Test Title"
    repo.save_tasks.assert_called_once_with([task])

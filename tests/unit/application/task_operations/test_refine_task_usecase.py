from unittest.mock import MagicMock

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from domain.task_management.task import Task, TaskCategory
from domain.task_management.task_repository import TaskRepository


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

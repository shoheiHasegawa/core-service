from unittest.mock import Mock

from application.task_management.task_management_service import TaskManagementService
from domain.task_management.task import Task, TaskCategory


def test_register_task():
    """[TASK-01]"""
    repo = Mock()
    service = TaskManagementService(repo)
    task = service.register_task("Test Title", "Test Description")
    assert task.title == "Test Title"
    repo.save_tasks.assert_called_once_with([task])


def test_refine_task():
    """[TASK-01]"""
    repo = Mock()
    service = TaskManagementService(repo)
    task = Task(id="task_id_123", title="Mock", category=TaskCategory.MUST, estimated_minutes=30)
    repo.get_tasks_by_ids.return_value = [task]

    refined = service.refine_task("task_id_123")
    assert refined.id == "task_id_123"
    repo.save_tasks.assert_called_once_with([task])


def test_refine_task_not_found():
    """[TASK-01]"""
    repo = Mock()
    service = TaskManagementService(repo)
    repo.get_tasks_by_ids.return_value = []

    refined = service.refine_task("task_id_456")
    assert refined is None

from unittest.mock import MagicMock

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from application.task_operations.task_operations_service import TaskOperationsService
from domain.task_management.task import Task, TaskCategory


def test_task_operations_service():
    """[TO-REG-01][TO-REF-01]"""
    reg = MagicMock(spec=RegisterTaskUseCase)
    ref = MagicMock(spec=RefineTaskUseCase)

    service = TaskOperationsService(register_task_usecase=reg, refine_task_usecase=ref)

    mock_task = Task(id="task-1", title="Title", category=TaskCategory.MUST, estimated_minutes=45)
    reg.execute.return_value = mock_task
    result_reg = service.register_task("Title", estimated_minutes=45)
    assert result_reg.id == "task-1"
    reg.execute.assert_called_once_with("Title", estimated_minutes=45)

    ref.execute.return_value = mock_task
    result_ref = service.refine_task(task_id="task-1", title="New Title")
    assert result_ref.id == "task-1"
    ref.execute.assert_called_once_with(task_id="task-1", title="New Title")

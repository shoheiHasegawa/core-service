from unittest.mock import MagicMock

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from application.task_operations.task_operations_service import TaskOperationsService


def test_task_operations_service():
    """[TO-REG-01]"""
    reg = MagicMock(spec=RegisterTaskUseCase)
    ref = MagicMock(spec=RefineTaskUseCase)

    service = TaskOperationsService(register_task_usecase=reg, refine_task_usecase=ref)

    reg.execute.return_value = None
    assert service.register_task("T", "D") is None
    reg.execute.assert_called_once_with("T", "D")

    ref.execute.return_value = None
    assert service.refine_task("ID") is None
    ref.execute.assert_called_once_with("ID")

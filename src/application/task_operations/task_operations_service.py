from typing import Optional

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from domain.task_management.task import Task


class TaskOperationsService:
    """
    Facade for Task Operations feature.
    Provides entry points for register_task and refine_task.
    Delegates actual logic to UseCases.
    """

    def __init__(self, register_task_usecase: RegisterTaskUseCase, refine_task_usecase: RefineTaskUseCase):
        self.register_task_usecase = register_task_usecase
        self.refine_task_usecase = refine_task_usecase

    def register_task(self, *args, **kwargs) -> Task:
        return self.register_task_usecase.execute(*args, **kwargs)

    def refine_task(self, *args, **kwargs) -> Optional[Task]:
        return self.refine_task_usecase.execute(*args, **kwargs)

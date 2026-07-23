from typing import Optional

from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task


class RefineTaskUseCase:
    def __init__(self, task_repository: Optional[TaskRepository] = None):
        self.task_repository = task_repository

    def execute(self, task_id: str) -> Optional[Task]:
        if not self.task_repository:
            return None

        tasks = self.task_repository.get_tasks_by_ids([task_id])
        if not tasks:
            return None

        task = tasks[0]
        self.task_repository.save_tasks([task])

        return task

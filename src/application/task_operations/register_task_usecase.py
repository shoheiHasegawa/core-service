import uuid
from typing import Optional

from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task, TaskCategory, TaskType


class RegisterTaskUseCase:
    def __init__(self, task_repository: Optional[TaskRepository] = None):
        self.task_repository = task_repository

    def execute(
        self,
        title: str,
        description: str,
        category: Optional[TaskCategory] = None,
        estimated_minutes: int = 30,
        reference_id: Optional[str] = None,
        task_type: Optional[TaskType] = None,
    ) -> Task:
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            category=category if category is not None else TaskCategory.SHOULD,
            estimated_minutes=estimated_minutes,
            reference_id=reference_id,
            task_type=task_type if task_type is not None else TaskType.ONE_OFF,
        )
        if self.task_repository:
            self.task_repository.save_tasks([task])
        return task

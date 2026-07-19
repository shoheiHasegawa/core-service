import uuid
from typing import Optional

from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task, TaskCategory, TaskType


class TaskManagementService:
    def __init__(self, task_repo: Optional[TaskRepository] = None):
        self.task_repo = task_repo

    def register_task(
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
        if self.task_repo:
            self.task_repo.save_tasks([task])
        return task

    def refine_task(self, task_id: str) -> Optional[Task]:
        if not self.task_repo:
            return None

        tasks = self.task_repo.get_tasks_by_ids([task_id])
        if not tasks:
            return None

        task = tasks[0]
        self.task_repo.save_tasks([task])

        return task

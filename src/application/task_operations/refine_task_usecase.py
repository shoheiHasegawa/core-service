from datetime import date
from typing import List, Optional

from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType
from domain.task_management.task_repository import TaskRepository


class RefineTaskUseCase:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(
        self,
        task_id: str,
        title: Optional[str] = None,
        category: Optional[TaskCategory] = None,
        estimated_minutes: Optional[int] = None,
        deadline: Optional[date] = None,
        target_date: Optional[date] = None,
        status: Optional[TaskStatus] = None,
        task_type: Optional[TaskType] = None,
        area_id: Optional[str] = None,
        energy_level: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        last_memo: Optional[str] = None,
    ) -> Task:
        tasks = self.task_repository.get_tasks_by_ids([task_id])
        if not tasks:
            raise ValueError(f"Task with id '{task_id}' not found.")

        task = tasks[0]

        if title is not None:
            if not title.strip():
                raise ValueError("Title must not be empty.")
            task.title = title.strip()

        if estimated_minutes is not None:
            if estimated_minutes <= 0:
                raise ValueError("Estimated minutes must be positive.")
            task.estimated_minutes = estimated_minutes

        if category is not None:
            task.category = category

        if deadline is not None:
            task.deadline = deadline

        if target_date is not None:
            task.target_date = target_date

        if status is not None:
            task.status = status

        if task_type is not None:
            task.task_type = task_type

        if area_id is not None:
            task.area_id = area_id

        if energy_level is not None:
            task.energy_level = energy_level

        if dependencies is not None:
            if task_id in dependencies:
                raise ValueError(f"Task '{task_id}' cannot depend on itself.")
            task.dependencies = dependencies

        if last_memo is not None:
            task.last_memo = last_memo

        self.task_repository.save_tasks([task])
        return task

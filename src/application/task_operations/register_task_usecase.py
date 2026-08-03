from datetime import date
from typing import List, Optional

from domain.system.uuid_generator import UUIDGenerator
from domain.task_management.task import Task, TaskCategory, TaskType
from domain.task_management.task_repository import TaskRepository
from infrastructure.system.system_uuid_generator import SystemUUIDGenerator


class RegisterTaskUseCase:
    def __init__(
        self,
        task_repository: TaskRepository,
        uuid_generator: Optional[UUIDGenerator] = None,
    ):
        self.task_repository = task_repository
        self.uuid_generator = uuid_generator or SystemUUIDGenerator()

    def execute(
        self,
        title: str,
        category: Optional[TaskCategory] = None,
        estimated_minutes: int = 30,
        deadline: Optional[date] = None,
        target_date: Optional[date] = None,
        task_type: Optional[TaskType] = None,
        area_id: str = "00_Unknown",
        reference_id: Optional[str] = None,
        energy_level: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        last_memo: Optional[str] = None,
        description: Optional[str] = None,  # 下位互換性のため維持し、last_memoにフォールバック
    ) -> Task:
        if not title or not title.strip():
            raise ValueError("Title must not be empty.")

        if estimated_minutes <= 0:
            raise ValueError("Estimated minutes must be positive.")

        memo = last_memo or description

        task = Task(
            id=self.uuid_generator.generate(),
            title=title.strip(),
            category=category if category is not None else TaskCategory.SHOULD,
            estimated_minutes=estimated_minutes,
            deadline=deadline,
            target_date=target_date,
            task_type=task_type if task_type is not None else TaskType.ONE_OFF,
            area_id=area_id,
            reference_id=reference_id,
            energy_level=energy_level,
            dependencies=dependencies or [],
            last_memo=memo,
        )

        self.task_repository.save_tasks([task])
        return task

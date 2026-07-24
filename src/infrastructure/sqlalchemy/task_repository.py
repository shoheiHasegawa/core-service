import json
import logging
from datetime import date
from typing import List, Optional

from sqlalchemy.orm import Session

from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType
from domain.task_management.task_repository import TaskRepository
from infrastructure.sqlalchemy.task_model import TaskModel


class SqlTaskRepository(TaskRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_ready_tasks_for_date(self, target_date: date) -> List[Task]:
        models = (
            self.session.query(TaskModel)
            .filter(TaskModel.target_date == target_date, TaskModel.status != TaskStatus.COMPLETED.value)
            .all()
        )
        return [self._to_entity(m) for m in models]

    def get_tasks_by_ids(self, task_ids: List[str]) -> List[Task]:
        models = self.session.query(TaskModel).filter(TaskModel.id.in_(task_ids)).all()
        return [self._to_entity(m) for m in models]

    def save_tasks(self, tasks: List[Task]) -> None:
        for task in tasks:
            self._save_model(task)
        self.session.commit()

    def save(self, task: Task) -> None:
        self._save_model(task)
        self.session.commit()

    def _save_model(self, task: Task) -> None:
        model = self.session.query(TaskModel).filter_by(id=task.id).first()
        if not model:
            model = TaskModel(id=task.id)
            self.session.add(model)

        model.title = task.title
        model.category = task.category.value
        model.estimated_minutes = task.estimated_minutes
        model.task_type = task.task_type.value
        model.area_id = task.area_id
        model.cumulative_minutes = task.cumulative_minutes
        model.status = task.status.value
        model.actual_minutes = task.actual_minutes
        model.deadline = task.deadline
        model.target_date = task.target_date
        model.dependencies = json.dumps(task.dependencies)
        model.reference_id = task.reference_id

    def find_by_target_date(self, target_date: date) -> List[Task]:
        models = self.session.query(TaskModel).filter(TaskModel.target_date == target_date).all()
        return [self._to_entity(m) for m in models]

    def find_by_id(self, task_id: str) -> Optional[Task]:
        model = self.session.query(TaskModel).filter_by(id=task_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def _to_entity(self, model: TaskModel) -> Task:
        deps = []
        if model.dependencies:
            try:
                deps = json.loads(model.dependencies)
            except json.JSONDecodeError as e:
                logging.getLogger(__name__).error("Failed to parse dependencies for task %s: %s", model.id, e)
                raise ValueError(f"Data corruption detected in dependencies for task {model.id}: {e}")

        return Task(
            id=model.id,
            title=model.title,
            category=TaskCategory(model.category),
            estimated_minutes=model.estimated_minutes,
            task_type=TaskType(model.task_type),
            area_id=model.area_id,
            cumulative_minutes=model.cumulative_minutes,
            status=TaskStatus(model.status),
            actual_minutes=model.actual_minutes,
            deadline=model.deadline,
            target_date=model.target_date,
            dependencies=deps,
            reference_id=model.reference_id,
        )

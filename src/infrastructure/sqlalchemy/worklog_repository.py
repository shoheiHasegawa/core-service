from datetime import date
from typing import List

from sqlalchemy.orm import Session

from domain.task_management.task import Worklog
from domain.task_management.worklog_repository import WorklogRepository
from infrastructure.sqlalchemy.worklog_model import WorklogModel


class SQLAlchemyWorklogRepository(WorklogRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, worklog: Worklog) -> None:
        model = self.session.query(WorklogModel).filter_by(id=worklog.id).first()
        if not model:
            # If not found by ID, try to find by task and date for upsert behavior
            if worklog.target_date:
                model = (
                    self.session.query(WorklogModel)
                    .filter_by(task_id=worklog.task_id, target_date=worklog.target_date)
                    .first()
                )
                if not model:
                    model = WorklogModel(id=worklog.id)
                    self.session.add(model)
                else:
                    worklog.id = model.id  # Sync back the existing ID
            else:
                model = WorklogModel(id=worklog.id)
                self.session.add(model)

        model.task_id = worklog.task_id
        if worklog.target_date:
            model.target_date = worklog.target_date
        model.minutes = worklog.minutes
        model.memo = worklog.memo
        model.area_id = worklog.area_id
        model.category = worklog.category.value
        model.task_type = worklog.task_type.value
        model.is_completed = worklog.is_completed
        self.session.commit()

    def find_by_task_and_date(self, task_id: str, target_date: date) -> List[Worklog]:
        from domain.task_management.task import TaskCategory, TaskType

        models = (
            self.session.query(WorklogModel)
            .filter(WorklogModel.task_id == task_id, WorklogModel.target_date == target_date)
            .all()
        )
        return [
            Worklog(
                id=m.id,
                task_id=m.task_id,
                minutes=m.minutes,
                is_completed=m.is_completed,
                target_date=m.target_date,
                memo=m.memo,
                area_id=m.area_id,
                category=TaskCategory(m.category) if m.category else TaskCategory.MUST,
                task_type=TaskType(m.task_type) if m.task_type else TaskType.ONE_OFF,
            )
            for m in models
        ]

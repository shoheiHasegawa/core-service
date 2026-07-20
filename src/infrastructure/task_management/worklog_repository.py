from datetime import date
from typing import List

from sqlalchemy.orm import Session

from domain.task_management.repository import WorklogRepository
from domain.task_management.task import Worklog
from infrastructure.db.models import WorklogModel


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
        model.category = worklog.category
        model.task_type = worklog.task_type
        model.is_completed = worklog.is_completed
        self.session.commit()

    def find_by_task_and_date(self, task_id: str, target_date: date) -> List[Worklog]:
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
                category=m.category,
                task_type=m.task_type,
            )
            for m in models
        ]

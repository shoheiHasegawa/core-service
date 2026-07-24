from datetime import date
from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from domain.task_management.recurring_task import RecurringTask
from domain.task_management.recurring_task_repository import RecurringTaskRepository
from domain.task_management.task import TaskCategory
from infrastructure.sqlalchemy.recurring_task_model import RecurringTaskModel


class SqlRecurringTaskRepository(RecurringTaskRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, recurring_task: RecurringTask) -> None:
        model = self.session.query(RecurringTaskModel).filter_by(id=recurring_task.id).one_or_none()
        if not model:
            model = RecurringTaskModel(id=recurring_task.id)
            self.session.add(model)

        model.name = recurring_task.name
        model.rule_type = recurring_task.rule_type
        model.cron_schedule = recurring_task.cron_schedule
        model.start_time = recurring_task.start_time
        model.end_time = recurring_task.end_time
        model.duration_minutes = recurring_task.duration_minutes
        model.category = recurring_task.category.value
        model.valid_from = recurring_task.valid_from
        model.valid_until = recurring_task.valid_until
        model.day_context = recurring_task.day_context

    def find_active_by_date(self, target_date: date) -> List[RecurringTask]:
        # valid_from が null または target_date 以下
        # かつ valid_until が null または target_date 以上
        query = self.session.query(RecurringTaskModel).filter(
            or_(RecurringTaskModel.valid_from.is_(None), RecurringTaskModel.valid_from <= target_date),
            or_(RecurringTaskModel.valid_until.is_(None), RecurringTaskModel.valid_until >= target_date),
        )

        models = query.all()
        tasks = []
        for model in models:
            task = RecurringTask(
                id=model.id,
                name=model.name,
                rule_type=model.rule_type,
                cron_schedule=model.cron_schedule,
                start_time=model.start_time,
                end_time=model.end_time,
                duration_minutes=model.duration_minutes,
                category=TaskCategory(model.category),
                valid_from=model.valid_from,
                valid_until=model.valid_until,
                day_context=model.day_context,
            )
            tasks.append(task)

        return tasks

from sqlalchemy import Column, Date, Integer, String

from .base import Base


class RecurringTaskModel(Base):
    __tablename__ = "recurring_tasks"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    rule_type = Column(String, nullable=False)
    cron_schedule = Column(String, nullable=False)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    valid_from = Column(Date, nullable=True)
    valid_until = Column(Date, nullable=True)
    day_context = Column(String, nullable=False, default="ANY")

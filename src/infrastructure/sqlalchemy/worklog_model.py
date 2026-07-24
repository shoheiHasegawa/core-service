from sqlalchemy import Boolean, Column, Date, Integer, String, UniqueConstraint

from .base import Base


class WorklogModel(Base):
    __tablename__ = "worklogs"
    __table_args__ = (UniqueConstraint("task_id", "target_date", name="uq_worklog_task_date"),)

    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    target_date = Column(Date, nullable=False)
    minutes = Column(Integer, nullable=False)
    memo = Column(String, nullable=True)
    area_id = Column(String, nullable=False, default="00_Unknown")
    category = Column(String, nullable=False, default="M")
    task_type = Column(String, nullable=False, default="ONE_OFF")
    is_completed = Column(Boolean, nullable=False, default=False)

from sqlalchemy import Column, Date, Integer, String

from .base import Base


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    estimated_minutes = Column(Integer, nullable=False)
    task_type = Column(String, nullable=False, default="ONE_OFF")
    area_id = Column(String, nullable=False, default="00_Unknown")
    cumulative_minutes = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="TODO")
    actual_minutes = Column(Integer, nullable=False, default=0)
    deadline = Column(Date, nullable=True)
    target_date = Column(Date, nullable=True)
    dependencies = Column(String, nullable=False, default="")
    reference_id = Column(String, nullable=True)
    last_memo = Column(String, nullable=True)
    energy_level = Column(String, nullable=True)

from sqlalchemy import Boolean, Column, Date, Integer, String, UniqueConstraint, event
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


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


def setup_sqlite_pragma(engine):
    """
    SQLiteエンジンに対してWALモードなどのPRAGMA設定を適用します。
    DI経由で生成されたエンジンを渡して初期化してください。
    """

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()

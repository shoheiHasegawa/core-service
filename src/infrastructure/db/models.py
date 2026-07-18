from sqlalchemy import Column, Date, Integer, String, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker


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

class WorklogModel(Base):
    __tablename__ = "worklogs"

    id = Column(String, primary_key=True)
    task_id = Column(String, nullable=False)
    target_date = Column(Date, nullable=False)
    minutes = Column(Integer, nullable=False)
    memo = Column(String, nullable=True)

# Engine setup
engine = create_engine("sqlite:///you_inc_ops.db")

@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

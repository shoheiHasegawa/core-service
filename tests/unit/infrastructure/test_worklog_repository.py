from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from domain.task_management.task import Worklog
from infrastructure.db.models import Base
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)
    engine.dispose()


def test_worklog_save_and_find(session):
    """[TM-PLAN-01]"""
    repo = SQLAlchemyWorklogRepository(session)

    worklog = Worklog(id="w1", task_id="task-1", minutes=30, target_date=date(2026, 7, 19))

    # Save worklog
    repo.save(worklog)

    # Find by task and date
    found = repo.find_by_task_and_date("task-1", date(2026, 7, 19))
    assert len(found) == 1
    assert found[0].task_id == "task-1"
    assert found[0].minutes == 30
    assert found[0].target_date == date(2026, 7, 19)


def test_worklog_update(session):
    """[TM-PLAN-01]"""
    repo = SQLAlchemyWorklogRepository(session)

    worklog1 = Worklog(id="w1", task_id="task-1", minutes=30, target_date=date(2026, 7, 19))
    repo.save(worklog1)

    # Update worklog with same task_id and target_date but no ID
    # Since find_by_task_and_date logic in save does an upsert
    worklog2 = Worklog(id="w2", task_id="task-1", minutes=50, target_date=date(2026, 7, 19))
    repo.save(worklog2)

    found = repo.find_by_task_and_date("task-1", date(2026, 7, 19))
    assert len(found) == 1
    assert found[0].minutes == 50

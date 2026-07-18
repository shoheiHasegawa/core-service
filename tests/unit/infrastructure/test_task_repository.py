from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Assuming we have these in infrastructure
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType
from infrastructure.db.models import Base
from infrastructure.task_management.task_repository import TaskRepository


@pytest.fixture
def session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(engine)


def test_save_and_find_by_target_date(session):
    """[SCENARIO-01]"""
    """
    [SCENARIO-INFRA-01] TaskRepository can save a task and find it by target_date.
    """
    repository = TaskRepository(session)
    task = Task(
        id="t-repo-1",
        title="Repo Test Task",
        category=TaskCategory.MUST,
        estimated_minutes=60,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 18),
        dependencies=[],
        task_type=TaskType.ONE_OFF,
        area_id="00_Unknown",
        cumulative_minutes=0,
        reference_id="ref-123",
    )

    # 保存
    repository.save(task)

    # 検索
    tasks = repository.find_by_target_date(date(2026, 7, 18))

    assert len(tasks) == 1
    assert tasks[0].id == "t-repo-1"
    assert tasks[0].title == "Repo Test Task"
    assert tasks[0].reference_id == "ref-123"


def test_find_by_id(session):
    """[SCENARIO-01]"""
    """
    [SCENARIO-INFRA-02] TaskRepository can find a task by id.
    """
    repository = TaskRepository(session)
    task = Task(
        id="t-repo-2",
        title="Repo Test Task 2",
        category=TaskCategory.WANT,
        estimated_minutes=30,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 19),
        dependencies=[],
    )

    repository.save(task)

    found_task = repository.find_by_id("t-repo-2")

    assert found_task is not None
    assert found_task.id == "t-repo-2"
    assert found_task.title == "Repo Test Task 2"

def test_get_ready_tasks_for_date(session):
    """[SCENARIO-01]"""
    repository = TaskRepository(session)
    task1 = Task(
        id="t-ready-1", title="Task 1", category=TaskCategory.MUST,
        estimated_minutes=30, target_date=date(2026, 7, 19), status=TaskStatus.TODO
    )
    task2 = Task(
        id="t-ready-2", title="Task 2", category=TaskCategory.SHOULD,
        estimated_minutes=30, target_date=date(2026, 7, 19), status=TaskStatus.COMPLETED
    )
    repository.save_tasks([task1, task2])

    tasks = repository.get_ready_tasks_for_date(date(2026, 7, 19))
    assert len(tasks) == 1
    assert tasks[0].id == "t-ready-1"

def test_get_tasks_by_ids(session):
    """[SCENARIO-01]"""
    repository = TaskRepository(session)
    task1 = Task(id="t-id-1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=30)
    task2 = Task(id="t-id-2", title="Task 2", category=TaskCategory.SHOULD, estimated_minutes=30)
    repository.save_tasks([task1, task2])

    tasks = repository.get_tasks_by_ids(["t-id-1"])
    assert len(tasks) == 1
    assert tasks[0].id == "t-id-1"

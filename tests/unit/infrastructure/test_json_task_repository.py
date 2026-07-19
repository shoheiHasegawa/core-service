from datetime import date
from pathlib import Path

from domain.task_management.task import Task, TaskCategory, TaskStatus
from infrastructure.json_task_repository import JsonTaskRepository


def test_json_task_repository_save_and_retrieve_tasks(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-01] JSON Task Repository should save and retrieve tasks properly.
    """
    repo = JsonTaskRepository(tmp_path)

    task1 = Task(
        id="task_1",
        title="Test Task 1",
        category=TaskCategory.MUST,
        estimated_minutes=30,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 6),
        dependencies=[],
    )

    # Save the task
    repo.save_tasks([task1])

    # Check if file exists
    assert (tmp_path / "task_1.json").exists()

    # Retrieve the tasks
    tasks = repo.get_ready_tasks_for_date(date(2026, 7, 6))
    assert len(tasks) == 1
    assert tasks[0].id == "task_1"
    assert tasks[0].title == "Test Task 1"


def test_json_task_repository_ignores_completed_tasks(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-02] JSON Task Repository should ignore completed tasks when retrieving ready tasks.
    """
    repo = JsonTaskRepository(tmp_path)

    task1 = Task(
        id="task_1",
        title="Test Task 1",
        category=TaskCategory.MUST,
        estimated_minutes=30,
        status=TaskStatus.COMPLETED,
        actual_minutes=30,
        deadline=None,
        target_date=date(2026, 7, 6),
        dependencies=[],
    )

    repo.save_tasks([task1])
    tasks = repo.get_ready_tasks_for_date(date(2026, 7, 6))

    # Completed tasks should be filtered out
    assert len(tasks) == 0


def test_json_task_repository_handles_malformed_json(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-03] JSON Task Repository should raise ValueError on malformed JSON files.
    """
    import pytest

    repo = JsonTaskRepository(tmp_path)
    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text("{ invalid json ")

    with pytest.raises(ValueError, match="Data corruption"):
        repo.get_ready_tasks_for_date(date(2026, 7, 6))


def test_json_task_repository_filters_by_target_date(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-04] JSON Task Repository must filter out tasks that do not match the target_date.
    """
    repo = JsonTaskRepository(tmp_path)

    task_today = Task(
        id="t1",
        title="Today",
        category=TaskCategory.MUST,
        estimated_minutes=10,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 6),
        dependencies=[],
    )
    task_tomorrow = Task(
        id="t2",
        title="Tomorrow",
        category=TaskCategory.MUST,
        estimated_minutes=10,
        status=TaskStatus.TODO,
        actual_minutes=0,
        deadline=None,
        target_date=date(2026, 7, 7),
        dependencies=[],
    )

    repo.save_tasks([task_today, task_tomorrow])

    tasks = repo.get_ready_tasks_for_date(date(2026, 7, 6))
    assert len(tasks) == 1
    assert tasks[0].id == "t1"


def test_json_task_repository_handles_missing_keys_and_invalid_values(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-05] Missing keys (KeyError) or invalid enum values (ValueError) should raise ValueError.
    """
    import pytest

    repo = JsonTaskRepository(tmp_path)

    # Missing 'title' key (KeyError)
    missing_key_file = tmp_path / "missing.json"
    missing_key_file.write_text('{"id": "t3", "category": "Work", "estimated_minutes": 10}')

    with pytest.raises(ValueError, match="Data corruption"):
        repo.get_ready_tasks_for_date(date(2026, 7, 6))


def test_json_task_repository_initializes_missing_directory(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-06] The repository should create the target directory if it does not exist.
    """
    new_dir = tmp_path / "new_nested_dir"
    assert not new_dir.exists()

    JsonTaskRepository(new_dir)
    assert new_dir.exists()


def test_json_task_repository_get_tasks_by_ids(tmp_path: Path):
    """[SCENARIO-01]"""
    """
    [SCENARIO-07] The repository should retrieve tasks by their IDs.
    """
    repo = JsonTaskRepository(tmp_path)

    task1 = Task(id="t1", title="T1", category=TaskCategory.MUST, estimated_minutes=10)
    task2 = Task(id="t2", title="T2", category=TaskCategory.SHOULD, estimated_minutes=20)

    repo.save_tasks([task1, task2])

    tasks = repo.get_tasks_by_ids(["t1", "t3"])
    assert len(tasks) == 1
    assert tasks[0].id == "t1"


def test_json_task_repository_get_tasks_by_ids_malformed(tmp_path: Path):
    """[SCENARIO-01]"""
    import pytest

    repo = JsonTaskRepository(tmp_path)
    malformed = tmp_path / "t_malformed.json"
    malformed.write_text("{ invalid json")

    with pytest.raises(ValueError, match="Data corruption"):
        repo.get_tasks_by_ids(["t_malformed"])

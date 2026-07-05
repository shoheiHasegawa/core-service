from datetime import date
from pathlib import Path

from domain.action_pipeline.task import EnergyLevel, Task, TaskCategory, TaskStatus
from infrastructure.json_task_repository import JsonTaskRepository


def test_json_task_repository_save_and_retrieve_tasks(tmp_path: Path):
    """
    [SCENARIO-01] JSON Task Repository should save and retrieve tasks properly.
    """
    repo = JsonTaskRepository(tmp_path)

    task1 = Task(
        id="task_1",
        title="Test Task 1",
        category=TaskCategory.MUST,
        energy_level=EnergyLevel.HIGH,
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
    """
    [SCENARIO-02] JSON Task Repository should ignore completed tasks when retrieving ready tasks.
    """
    repo = JsonTaskRepository(tmp_path)

    task1 = Task(
        id="task_1",
        title="Test Task 1",
        category=TaskCategory.MUST,
        energy_level=EnergyLevel.HIGH,
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
    """
    [SCENARIO-03] JSON Task Repository should handle malformed JSON files gracefully without crashing.
    """
    repo = JsonTaskRepository(tmp_path)
    malformed_file = tmp_path / "malformed.json"
    malformed_file.write_text("{ invalid json ")

    tasks = repo.get_ready_tasks_for_date(date(2026, 7, 6))
    assert len(tasks) == 0


def test_json_task_repository_filters_by_target_date(tmp_path: Path):
    """
    [SCENARIO-04] JSON Task Repository must filter out tasks that do not match the target_date.
    """
    repo = JsonTaskRepository(tmp_path)

    task_today = Task(
        id="t1",
        title="Today",
        category=TaskCategory.MUST,
        energy_level=EnergyLevel.HIGH,
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
        energy_level=EnergyLevel.HIGH,
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
    """
    [SCENARIO-05] Missing keys (KeyError) or invalid enum values (ValueError) should skip the file without crashing.
    """
    repo = JsonTaskRepository(tmp_path)

    # Missing 'title' key (KeyError)
    missing_key_file = tmp_path / "missing.json"
    missing_key_file.write_text('{"id": "t3", "category": "Work", "energy_level": "High", "estimated_minutes": 10}')

    # Invalid enum value (ValueError)
    invalid_enum_file = tmp_path / "invalid.json"
    invalid_enum_file.write_text(
        '{"id": "t4", "title": "Invalid", "category": "UNKNOWN", "energy_level": "High", "estimated_minutes": 10}'
    )

    # This should skip both and return 0 tasks, not crash
    tasks = repo.get_ready_tasks_for_date(date(2026, 7, 6))
    assert len(tasks) == 0


def test_json_task_repository_initializes_missing_directory(tmp_path: Path):
    """
    [SCENARIO-06] The repository should create the target directory if it does not exist.
    """
    new_dir = tmp_path / "new_nested_dir"
    assert not new_dir.exists()

    JsonTaskRepository(new_dir)
    assert new_dir.exists()

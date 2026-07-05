from datetime import date
from unittest.mock import Mock

from application.action_pipeline.daily_planning_service import DailyPlanningService
from domain.action_pipeline.task import EnergyLevel, Task, TaskCategory, WarningFlag


def test_scenario_02_wip_limit_exceeded():
    """[SCENARIO-02] WIP制限（3つ）を超過するMUSTタスクは弾かれること"""

    # ... (We will use multi_replace instead to be safe since we need to replace 3 specific docstrings)
    task_repo = Mock()
    tasks = [
        Task(
            id=f"t{i}",
            title=f"Must Task {i}",
            category=TaskCategory.MUST,
            energy_level=EnergyLevel.HIGH,
            estimated_minutes=30,
        )
        for i in range(5)  # 5 MUST tasks
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    service = DailyPlanningService(task_repo, Mock(), Mock())

    briefing = service.generate_today_plan(date.today())
    must_scheduled = [t for t in briefing.scheduled_tasks if t.category == TaskCategory.MUST]

    assert len(must_scheduled) == 3


def test_scenario_03_w_ratio_low():
    """[SCENARIO-03] Wタスクの割合が20%未満の場合、W_ratio_lowフラグが立つこと"""
    task_repo = Mock()
    tasks = [
        Task(id="t1", title="Must 1", category=TaskCategory.MUST, energy_level=EnergyLevel.HIGH, estimated_minutes=60),
        Task(id="t2", title="Must 2", category=TaskCategory.MUST, energy_level=EnergyLevel.HIGH, estimated_minutes=60),
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    service = DailyPlanningService(task_repo, Mock(), Mock())

    briefing = service.generate_today_plan(date.today())
    assert WarningFlag.W_RATIO_LOW in briefing.warning_flags


def test_scenario_05_context_batching():
    """[SCENARIO-05] コンテキストスイッチを防ぐため、EnergyLevelごとにバッチ化されること"""
    task_repo = Mock()
    tasks = [
        Task(id="1", title="H1", category=TaskCategory.MUST, energy_level=EnergyLevel.HIGH, estimated_minutes=30),
        Task(id="2", title="L1", category=TaskCategory.SHOULD, energy_level=EnergyLevel.LOW, estimated_minutes=30),
        Task(id="3", title="H2", category=TaskCategory.MUST, energy_level=EnergyLevel.HIGH, estimated_minutes=30),
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    service = DailyPlanningService(task_repo, Mock(), Mock())

    briefing = service.generate_today_plan(date.today())
    energies = [t.energy_level for t in briefing.scheduled_tasks]

    # H1, H2 が連続するようにソートされていること
    assert energies == [EnergyLevel.HIGH, EnergyLevel.HIGH, EnergyLevel.LOW]

from datetime import date
from unittest.mock import MagicMock

from application.daily_planning.plan_day_usecase import PlanDayUseCase
from domain.task_management.briefing_gateway import BriefingGateway
from domain.task_management.schedule_gateway import ScheduleGateway
from domain.task_management.task import Task, TaskCategory, WarningFlag
from domain.task_management.task_repository import TaskRepository


def test_scenario_02_wip_limit_exceeded():
    """[TM-PLAN-02] WIP制限（3つ）を超過するMUSTタスクは弾かれること"""
    task_repo = MagicMock(spec=TaskRepository)
    tasks = [
        Task(id=f"t{i}", title=f"Must Task {i}", category=TaskCategory.MUST, estimated_minutes=30, area_id="01_Work")
        for i in range(5)  # 5 MUST tasks
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    usecase = PlanDayUseCase(
        task_repo,
        MagicMock(spec=ScheduleGateway),
        MagicMock(spec=BriefingGateway),
    )

    briefing = usecase.execute(date.today())
    must_scheduled = [t for t in briefing.scheduled_tasks if t.category == TaskCategory.MUST and t.id != "sleep"]

    assert len(must_scheduled) == 3


def test_scenario_03_w_ratio_low():
    """[TM-PLAN-03] Wタスクの割合が20%未満の場合、W_ratio_lowフラグが立つこと"""
    task_repo = MagicMock(spec=TaskRepository)
    tasks = [
        Task(id="t1", title="Must 1", category=TaskCategory.MUST, estimated_minutes=60),
        Task(id="t2", title="Must 2", category=TaskCategory.MUST, estimated_minutes=60),
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    usecase = PlanDayUseCase(
        task_repo,
        MagicMock(spec=ScheduleGateway),
        MagicMock(spec=BriefingGateway),
    )

    briefing = usecase.execute(date.today())
    assert WarningFlag.W_RATIO_LOW in briefing.warning_flags

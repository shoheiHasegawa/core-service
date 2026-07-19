from datetime import date
from unittest.mock import MagicMock

from application.task_management.daily_action_service import DailyActionService
from domain.task_management.repository import BriefingRepository, ScheduleGateway, TaskRepository, WorklogRepository
from domain.task_management.task import Task, TaskCategory, TaskStatus, WarningFlag, Worklog


def test_scenario_02_wip_limit_exceeded():
    """[TASK-02] WIP制限（3つ）を超過するMUSTタスクは弾かれること"""

    task_repo = MagicMock(spec=TaskRepository)
    tasks = [
        Task(
            id=f"t{i}",
            title=f"Must Task {i}",
            category=TaskCategory.MUST,
            estimated_minutes=30,
        )
        for i in range(5)  # 5 MUST tasks
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    service = DailyActionService(
        task_repo,
        MagicMock(spec=ScheduleGateway),
        MagicMock(spec=BriefingRepository),
        MagicMock(spec=WorklogRepository),
    )

    briefing = service.plan_day(date.today())
    must_scheduled = [t for t in briefing.scheduled_tasks if t.category == TaskCategory.MUST]

    assert len(must_scheduled) == 3


def test_scenario_03_w_ratio_low():
    """[TASK-03] Wタスクの割合が20%未満の場合、W_ratio_lowフラグが立つこと"""
    task_repo = MagicMock(spec=TaskRepository)
    tasks = [
        Task(id="t1", title="Must 1", category=TaskCategory.MUST, estimated_minutes=60),
        Task(id="t2", title="Must 2", category=TaskCategory.MUST, estimated_minutes=60),
    ]
    task_repo.get_ready_tasks_for_date.return_value = tasks
    service = DailyActionService(
        task_repo,
        MagicMock(spec=ScheduleGateway),
        MagicMock(spec=BriefingRepository),
        MagicMock(spec=WorklogRepository),
    )

    briefing = service.plan_day(date.today())
    assert WarningFlag.W_RATIO_LOW in briefing.warning_flags


def test_record_worklogs():
    """[TASK-01] record_worklogsが既存のWorklogを考慮して冪等に動作すること"""
    task_repo = MagicMock(spec=TaskRepository)
    worklog_repo = MagicMock(spec=WorklogRepository)
    service = DailyActionService(
        task_repo, MagicMock(spec=ScheduleGateway), MagicMock(spec=BriefingRepository), worklog_repo
    )

    task = Task(id="t1", title="Must 1", category=TaskCategory.MUST, estimated_minutes=60, actual_minutes=10)
    task_repo.get_tasks_by_ids.return_value = [task]

    # 既存のWorklogとして20分が記録されている
    existing_worklog = MagicMock(spec=Worklog)
    existing_worklog.minutes = 20
    worklog_repo.find_by_task_and_date.return_value = [existing_worklog]

    # 画面からは30分として飛んでくる (差分は +10)
    new_worklog = Worklog(id="w1", task_id="t1", minutes=30, is_completed=True)
    service.record_worklogs(date.today(), [new_worklog])

    # 差分の10分が加算されて20分になること
    assert task.actual_minutes == 20
    assert task.status == TaskStatus.COMPLETED
    task_repo.save_tasks.assert_called_once_with([task])
    worklog_repo.save.assert_called_once_with(new_worklog)

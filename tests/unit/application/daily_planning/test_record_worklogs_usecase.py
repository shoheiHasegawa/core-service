from datetime import date
from unittest.mock import MagicMock

from application.daily_planning.record_worklogs_usecase import RecordWorklogsUseCase
from domain.task_management.repository import TaskRepository, WorklogRepository
from domain.task_management.task import Task, TaskCategory, TaskStatus, Worklog


def test_record_worklogs():
    """[TM-PLAN-01] record_worklogsが既存のWorklogを考慮して冪等に動作すること"""
    task_repo = MagicMock(spec=TaskRepository)
    worklog_repo = MagicMock(spec=WorklogRepository)
    usecase = RecordWorklogsUseCase(task_repo, worklog_repo)

    task = Task(id="t1", title="Must 1", category=TaskCategory.MUST, estimated_minutes=60, actual_minutes=10)
    task_repo.get_tasks_by_ids.return_value = [task]

    # 既存のWorklogとして20分が記録されている
    existing_worklog = MagicMock(spec=Worklog)
    existing_worklog.minutes = 20
    worklog_repo.find_by_task_and_date.return_value = [existing_worklog]

    # 画面からは30分として飛んでくる (差分は +10)
    new_worklog = Worklog(id="w1", task_id="t1", minutes=30, is_completed=True)
    usecase.execute(date.today(), [new_worklog])

    # 差分の10分が加算されて20分になること
    assert task.actual_minutes == 20
    assert task.status == TaskStatus.COMPLETED
    task_repo.save_tasks.assert_called_once_with([task])
    worklog_repo.save.assert_called_once_with(new_worklog)

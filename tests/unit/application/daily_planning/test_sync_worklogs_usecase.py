from unittest.mock import MagicMock

from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase
from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.task_management.task_repository import TaskRepository
from domain.task_management.worklog_repository import WorklogRepository


def test_sync_worklogs():
    """[TM-SYNC-04]"""
    dashboard_reader = MagicMock(spec=DashboardReader)
    worklog_repo = MagicMock(spec=WorklogRepository)

    dashboard_reader.get_recent_dashboards.return_value = [""]
    task_repo = MagicMock(spec=TaskRepository)
    usecase = SyncWorklogsUseCase(dashboard_reader, task_repo, worklog_repo)

    usecase.execute()

    assert dashboard_reader.get_recent_dashboards.call_count == 1

from unittest.mock import MagicMock

from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase
from domain.task_management.briefing_gateway import BriefingGateway
from domain.task_management.task_repository import TaskRepository
from domain.task_management.worklog_repository import WorklogRepository


def test_sync_worklogs():
    """[TM-SYNC-04]"""
    briefing_gateway = MagicMock(spec=BriefingGateway)
    worklog_repo = MagicMock(spec=WorklogRepository)

    briefing_gateway.get_recent_briefing_contents.return_value = [""]
    task_repo = MagicMock(spec=TaskRepository)
    usecase = SyncWorklogsUseCase(briefing_gateway, task_repo, worklog_repo)

    usecase.execute()

    assert briefing_gateway.get_recent_briefing_contents.call_count == 1

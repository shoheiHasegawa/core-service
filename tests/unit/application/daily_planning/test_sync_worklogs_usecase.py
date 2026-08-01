from datetime import date, datetime
from unittest.mock import MagicMock

from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase
from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.system.clock import Clock
from domain.system.uuid_generator import UUIDGenerator
from domain.task_management.briefing_markdown_parser import BriefingMarkdownParser
from domain.task_management.task import Task, TaskCategory, TaskStatus
from domain.task_management.task_repository import TaskRepository
from domain.task_management.worklog_repository import WorklogRepository


def test_sync_worklogs():
    """[TM-SYNC-04]"""
    dashboard_reader = MagicMock(spec=DashboardReader)
    worklog_repo = MagicMock(spec=WorklogRepository)
    task_repo = MagicMock(spec=TaskRepository)
    parser = BriefingMarkdownParser()

    clock = MagicMock(spec=Clock)
    clock.now.return_value = datetime(2026, 7, 31, 10, 0, 0)

    uuid_gen = MagicMock(spec=UUIDGenerator)
    uuid_gen.generate.return_value = "fake-uuid-1"

    # Dashboard with mixed tasks
    mock_dashboard_content = """# Daily Briefing (2026-07-31)
- [x] Task A (予定: 30m) <!-- id: task_a -->
- [ ] Task B (予定: 60m) <!-- id: task_b --> 45
  メモ: In progress
"""

    def mock_read_dashboard(filename):
        if filename == "Briefing_2026-07-31.md":
            return mock_dashboard_content
        return None

    dashboard_reader.read_dashboard.side_effect = mock_read_dashboard

    # Mock tasks
    task_a = Task(id="task_a", title="Task A", category=TaskCategory.MUST, estimated_minutes=30)
    task_b = Task(id="task_b", title="Task B", category=TaskCategory.SHOULD, estimated_minutes=60)

    def mock_find_by_id(task_id):
        if task_id == "task_a":
            return task_a
        elif task_id == "task_b":
            return task_b
        return None

    task_repo.find_by_id.side_effect = mock_find_by_id

    usecase = SyncWorklogsUseCase(dashboard_reader, task_repo, worklog_repo, parser, clock, uuid_gen)
    usecase.execute()

    # Assertions
    assert dashboard_reader.read_dashboard.call_count == 2  # Yesterday and today
    assert task_repo.find_by_id.call_count == 2
    assert task_repo.save.call_count == 2

    saved_tasks = [call.args[0] for call in task_repo.save.call_args_list]

    # Verify Task A was completed
    t_a = next(t for t in saved_tasks if t.id == "task_a")
    assert t_a.status == TaskStatus.COMPLETED
    assert t_a.actual_minutes == 30  # Fallback to estimated

    # Verify Task B was marked in progress and memo saved
    t_b = next(t for t in saved_tasks if t.id == "task_b")
    assert t_b.status == TaskStatus.IN_PROGRESS
    assert t_b.actual_minutes == 45
    assert t_b.last_memo == "In progress"

    # Verify worklogs created
    assert worklog_repo.save.call_count == 2
    saved_worklogs = [call.args[0] for call in worklog_repo.save.call_args_list]
    wl_b = next(wl for wl in saved_worklogs if wl.task_id == "task_b")
    assert wl_b.memo == "In progress"
    assert wl_b.target_date == date(2026, 7, 31)

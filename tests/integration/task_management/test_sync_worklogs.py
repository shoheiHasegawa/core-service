"""[TM-SYNC-04] 日次同期と実績（Worklog）作成のIntegration Test"""

from datetime import date

from freezegun import freeze_time
from integration.conftest import IntegrationTestContext

from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase
from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.task_management.task import Task, TaskCategory
from infrastructure.sqlalchemy.worklog_repository import SQLAlchemyWorklogRepository


class FakeDashboardReader(DashboardReader):
    def __init__(self):
        self.dashboards = {}
        self.read_dashboard_called = 0

    def publish(self, filename: str, content: str):
        self.dashboards[filename] = content

    def read_dashboard(self, filename: str) -> dict[str, str]:
        self.read_dashboard_called += 1
        return self.dashboards.get(filename)

    def delete_dashboard(self, filename: str) -> None:
        if filename in self.dashboards:
            del self.dashboards[filename]


@freeze_time("2026-07-22")
def test_sync_worklogs_integration(test_context: IntegrationTestContext):
    """[TM-SYNC-04] InboxディレクトリのBriefingファイルを読み込み、Worklogを作成する"""
    task_repo = test_context.task_repo
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)
    dashboard_reader = FakeDashboardReader()

    # Setup dashboards
    dashboard_reader.publish(
        "Briefing_2026-07-21.md", "# Daily Briefing (2026-07-21)\n- [x] Task Old (予定: 10m) <!-- id: t_old -->\n"
    )
    dashboard_reader.publish(
        "Briefing_2026-07-22.md", "# Daily Briefing (2026-07-22)\n- [x] Task 1 (予定: 30m) <!-- id: t1 -->\n"
    )

    from datetime import datetime

    from domain.task_management.briefing_markdown_parser import BriefingMarkdownParser
    from tests.integration.helpers.fake_clock import FakeClock
    from tests.integration.helpers.fake_uuid_generator import FakeUUIDGenerator

    clock = FakeClock(datetime(2026, 7, 22, 10, 0, 0))
    uuid_gen = FakeUUIDGenerator(["fake-wl-1", "fake-wl-2"])

    usecase = SyncWorklogsUseCase(dashboard_reader, task_repo, worklog_repo, BriefingMarkdownParser(), clock, uuid_gen)

    # 準備：DBにタスクを登録
    target_date = date(2026, 7, 22)
    task1 = Task(id="t1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=30, target_date=target_date)
    task_repo.save_tasks([task1])
    test_context.session.commit()

    # 実行
    usecase.execute()
    test_context.session.commit()

    # 検証：WorklogがDBに保存されているか
    worklogs = worklog_repo.find_by_task_and_date("t1", date(2026, 7, 22))
    assert len(worklogs) == 1
    assert worklogs[0].task_id == "t1"

    # read_dashboard が呼ばれたか検証
    assert dashboard_reader.read_dashboard_called == 2, "昨日と今日のダッシュボードが読み取られるべき"

    # 昨日のファイルや無関係のファイルがパースされたり異常動作を引き起こしていないことの検証
    worklogs_old = worklog_repo.find_by_task_and_date("t_old", date(2026, 7, 21))
    assert len(worklogs_old) == 0, "昨日のタスク(未DB登録)が無理にパース・保存されていてはいけない"

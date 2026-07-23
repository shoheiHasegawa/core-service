"""[TM-SYNC-04] 日次同期と実績（Worklog）作成のIntegration Test"""

from datetime import date

from freezegun import freeze_time
from integration.conftest import IntegrationTestContext

from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase
from domain.task_management.repository import BriefingGateway
from domain.task_management.task import DailyBriefing, Task, TaskCategory
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeBriefingGateway(BriefingGateway):
    def __init__(self):
        self.contents = [
            "# Daily Briefing (2026-07-22)\n- [x] Task 1 (予定: 30m) <!-- id: t1 -->\n",
            "# Daily Briefing (2026-07-21)\n- [x] Task Old (予定: 10m) <!-- id: t_old -->\n",
        ]
        self.get_recent_briefing_contents_called = 0

    def save(self, briefing: DailyBriefing) -> None:
        pass

    def get_recent_briefing_contents(self) -> list[str]:
        self.get_recent_briefing_contents_called += 1
        return self.contents


@freeze_time("2026-07-22")
def test_sync_worklogs_integration(test_context: IntegrationTestContext):
    """[TM-SYNC-04] InboxディレクトリのBriefingファイルを読み込み、Worklogを作成する"""
    task_repo = test_context.task_repo
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)
    fake_gateway = FakeBriefingGateway()

    # 準備：DBにタスクを登録
    target_date = date(2026, 7, 22)
    task1 = Task(id="t1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=30, target_date=target_date)
    task_repo.save_tasks([task1])
    test_context.session.commit()

    # サービス初期化
    service = SyncWorklogsUseCase(
        briefing_gateway=fake_gateway,
        task_repository=task_repo,
        worklog_repository=worklog_repo,
    )

    # 実行
    service.execute()
    test_context.session.commit()

    # 検証：WorklogがDBに保存されているか
    worklogs = worklog_repo.find_by_task_and_date("t1", date(2026, 7, 22))
    assert len(worklogs) == 1
    assert worklogs[0].task_id == "t1"

    # get_recent_briefing_contents が呼ばれたか検証
    assert fake_gateway.get_recent_briefing_contents_called == 1, "ダッシュボード内容を取得するメソッドが呼ばれるべき"

    # 昨日のファイルや無関係のファイルがパースされたり異常動作を引き起こしていないことの検証
    worklogs_old = worklog_repo.find_by_task_and_date("t_old", date(2026, 7, 21))
    assert len(worklogs_old) == 0, "昨日のタスク(未DB登録)が無理にパース・保存されていてはいけない"

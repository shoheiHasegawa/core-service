"""[TM-SYNC-04] 日次同期と実績（Worklog）作成のIntegration Test"""

from datetime import date

from integration.conftest import IntegrationTestContext

from application.mobile_vault.interfaces import MobileVaultGateway
from application.task_management.sync_worklogs_service import SyncWorklogsService
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeMobileVaultGateway(MobileVaultGateway):
    def __init__(self):
        self.files = {
            "Briefing_2026-07-22.md": "# Daily Briefing (2026-07-22)\n- [x] Task 1 (予定: 30m) <!-- id: t1 -->\n"
        }
        self.moved = []

    def save_file(self, content: str, filename: str) -> None:
        pass

    def save_inbox_file(self, content: str, filename: str) -> None:
        pass

    def save_dashboard_file(self, content: str, filename: str) -> None:
        pass

    def read_text(self, filepath: str) -> str:
        return self.files.get(filepath, "")

    def ensure_directory_exists(self, directory: str) -> None:
        pass

    def list_markdown_files(self) -> list[str]:
        return ["Briefing_2026-07-22.md"]

    def move_file(self, old_path: str, new_path: str) -> None:
        self.moved.append((old_path, new_path))
        if old_path in self.files:
            self.files[new_path] = self.files.pop(old_path)

    def delete_file(self, filepath: str) -> None:
        if filepath in self.files:
            del self.files[filepath]


def test_sync_worklogs_integration(test_context: IntegrationTestContext):
    """[TM-SYNC-04] InboxディレクトリのBriefingファイルを読み込み、Worklogを作成する"""
    task_repo = test_context.task_repo
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)
    fake_vault = FakeMobileVaultGateway()

    # 準備：DBにタスクを登録
    target_date = date(2026, 7, 22)
    task1 = Task(id="t1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=30, target_date=target_date)
    task_repo.save_tasks([task1])
    test_context.session.commit()

    # サービス初期化
    service = SyncWorklogsService(
        mobile_vault_gateway=fake_vault,
        task_repository=task_repo,
        worklog_repository=worklog_repo,
    )

    # 実行
    service.sync()
    test_context.session.commit()

    # 検証：WorklogがDBに保存されているか
    worklogs = worklog_repo.find_by_task_and_date("t1", date.today())
    assert len(worklogs) == 1
    assert worklogs[0].task_id == "t1"

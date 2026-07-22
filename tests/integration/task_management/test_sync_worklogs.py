"""[TM-SYNC-04] 日次同期と実績（Worklog）作成のIntegration Test"""

import pytest
from datetime import date

from integration.conftest import IntegrationTestContext
from application.mobile_vault.interfaces import MobileVaultRepository
from application.task_management.sync_worklogs_service import SyncWorklogsService
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeMobileVaultRepository(MobileVaultRepository):
    def __init__(self):
        self.files = {"/fake/inbox/Briefing_2026-07-22.md": "# Daily Briefing (2026-07-22)\n- [x] Task 1 (予定: 30m) <!-- id: t1 -->\n"}
        self.moved = []

    def save_file(self, content: str, directory: str, filename: str) -> None:
        pass

    def read_text(self, filepath: str) -> str:
        return self.files.get(filepath, "")

    def ensure_directory_exists(self, directory: str) -> None:
        pass

    def list_markdown_files(self, directory: str) -> list[str]:
        return ["Briefing_2026-07-22.md"]

    def move_file(self, old_path: str, new_path: str) -> None:
        self.moved.append((old_path, new_path))
        if old_path in self.files:
            self.files[new_path] = self.files.pop(old_path)

    def delete_file(self, filepath: str) -> None:
        if filepath in self.files:
            del self.files[filepath]


def test_sync_worklogs_integration(test_context: IntegrationTestContext):
    """[TM-SYNC-04] InboxディレクトリのBriefingファイルを読み込み、Worklogを作成し、ファイルをアーカイブする"""
    task_repo = test_context.task_repo
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)
    fake_vault = FakeMobileVaultRepository()

    # 準備：DBにタスクを登録
    target_date = date(2026, 7, 22)
    task1 = Task(id="t1", title="Task 1", category=TaskCategory.MUST, estimated_minutes=30, target_date=target_date)
    task_repo.save_tasks([task1])
    test_context.session.commit()

    # サービス初期化
    service = SyncWorklogsService(
        mobile_vault_repository=fake_vault,
        task_repository=task_repo,
        worklog_repository=worklog_repo,
        inbox_dir="/fake/inbox",
        archive_dir="/fake/archive"
    )

    # 実行
    service.sync()
    test_context.session.commit()

    # 検証：WorklogがDBに保存されているか
    worklogs = worklog_repo.find_by_task_and_date("t1", date.today())
    assert len(worklogs) == 1
    assert worklogs[0].task_id == "t1"

    # 検証：ファイルがアーカイブに移動されているか
    assert len(fake_vault.moved) == 1
    assert fake_vault.moved[0] == ("/fake/inbox/Briefing_2026-07-22.md", "/fake/archive/Briefing_2026-07-22.md")

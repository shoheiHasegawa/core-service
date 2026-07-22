"""[TM-SYNC-03] DailyBriefingのMarkdown連携 (Mobile Vault同期)"""

from datetime import date
from unittest.mock import Mock

from application.mobile_vault.interfaces import MobileVaultGateway
from domain.task_management.task import DailyBriefing, Task, WarningFlag
from infrastructure.task_management.briefing_gateway import MobileVaultBriefingGateway


def test_save_briefing_generates_markdown():
    """[TM-SYNC-03] DailyBriefingがMarkdown文字列に変換され、MobileVaultに保存されることを確認する"""
    mock_mobile_vault = Mock(spec=MobileVaultGateway)
    repo = MobileVaultBriefingGateway(mock_mobile_vault, "/fake/inbox")

    # 準備
    target_date = date(2026, 7, 22)
    task1 = Task(id="t1", title="Test Task 1", category="M", estimated_minutes=30)
    task2 = Task(id="t2", title="Test Task 2", category="S", estimated_minutes=60, last_memo="Carry over")
    briefing = DailyBriefing(
        target_date=target_date,
        scheduled_tasks=[task1, task2],
        deferred_tasks=[],
        warning_flags=[WarningFlag.W_RATIO_LOW],
    )

    # 実行
    repo.save(briefing)

    # 検証
    mock_mobile_vault.ensure_directory_exists.assert_called_with("/fake/inbox")

    expected_filename = "Briefing_2026-07-22.md"

    mock_mobile_vault.save_file.assert_called_once()
    call_args = mock_mobile_vault.save_file.call_args
    content, directory, filename = call_args[0]

    assert directory == "/fake/inbox"
    assert filename == expected_filename
    assert "# Daily Briefing (2026-07-22)" in content
    assert "## ⚠️ Warnings" in content
    assert "- W_RATIO_LOW" in content
    assert "- [ ] Test Task 1 (予定: 30m) <!-- id: t1 -->" in content
    assert "- [ ] Test Task 2 (予定: 60m) <!-- id: t2 -->" in content
    assert "前回メモ: Carry over" in content


def test_save_briefing_protection():
    """[TM-SYNC-03] ファイルが既に存在してもバックアップを取得せず、無条件で上書きを行う"""
    mock_mobile_vault = Mock(spec=MobileVaultGateway)

    repo = MobileVaultBriefingGateway(mock_mobile_vault, "/fake/inbox")

    target_date = date(2026, 7, 22)
    briefing = DailyBriefing(target_date=target_date, scheduled_tasks=[], deferred_tasks=[], warning_flags=[])

    # 実行
    repo.save(briefing)

    # 検証: save_fileが1回だけ呼ばれること
    assert mock_mobile_vault.save_file.call_count == 1

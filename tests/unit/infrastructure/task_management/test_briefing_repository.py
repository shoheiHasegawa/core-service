"""[TM-SYNC-03] DailyBriefingのMarkdown連携 (Mobile Vault同期)"""

from datetime import date
from unittest.mock import Mock

from application.mobile_vault.interfaces import MobileVaultRepository
from domain.task_management.task import DailyBriefing, Task, WarningFlag
from infrastructure.task_management.briefing_repository import MobileVaultBriefingRepository


def test_save_briefing_generates_markdown():
    """[TM-SYNC-03] DailyBriefingがMarkdown文字列に変換され、MobileVaultに保存されることを確認する"""
    mock_mobile_vault = Mock(spec=MobileVaultRepository)
    repo = MobileVaultBriefingRepository(mock_mobile_vault, "/fake/inbox")

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
    """[TM-SYNC-03] ファイルが既に存在する場合はバックアップを取得（move_fileまたはrename_file）し、再度保存を行う"""
    mock_mobile_vault = Mock(spec=MobileVaultRepository)

    # 1回目のsave_fileでFileExistsErrorを出し、2回目は成功するように設定
    mock_mobile_vault.save_file.side_effect = [FileExistsError("File already exists"), None]

    repo = MobileVaultBriefingRepository(mock_mobile_vault, "/fake/inbox")

    target_date = date(2026, 7, 22)
    briefing = DailyBriefing(target_date=target_date, scheduled_tasks=[], deferred_tasks=[], warning_flags=[])

    # 実行
    repo.save(briefing)

    # 検証: save_fileが2回呼ばれること
    assert mock_mobile_vault.save_file.call_count == 2
    # 検証: move_file または rename_file がバックアップのために呼ばれること（Mockにはmove_fileがある想定）
    mock_mobile_vault.move_file.assert_called_once()

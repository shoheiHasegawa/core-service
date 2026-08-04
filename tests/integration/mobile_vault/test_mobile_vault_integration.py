"""[MV-RECV-01][MV-RECV-02][MV-IDEM-01][MV-BOUND-01][MV-BOUND-02][MV-BOUND-03][MV-RECON-01][MV-FAULT-01][MV-FAULT-02][MV-INVAR-01][MV-INVAR-02] Mobile Vault Integration Tests"""

import tempfile
from pathlib import Path

import pytest

from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.peek_inbox_usecase import PeekInboxUseCase
from application.mobile_vault.process_inbox_item_usecase import ProcessInboxItemUseCase
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.second_brain_service import SecondBrainService
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.task_management.task import TaskCategory
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from infrastructure.local_file.local_file_second_brain_gateway import LocalFileSecondBrainGateway
from infrastructure.sqlalchemy.task_model import TaskModel
from tests.integration.conftest import IntegrationTestContext


def _create_harness(mobile_dir: str, mobile_img_dir: str, sb_dir: str, test_context: IntegrationTestContext):
    """結合テスト用ハーネスのセットアップ（実ファイル・実SQLite）"""
    mobile_gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, attachments_dir=mobile_img_dir)
    sb_gateway = LocalFileSecondBrainGateway(sb_dir)

    inbox_dir = Path(sb_dir) / "00_Inbox"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    template_path = Path(sb_dir) / "template.md"
    template_path.write_text("# {{TITLE}}\n{{BODY}}\ntags: []", encoding="utf-8")

    register_inbox_uc = RegisterInboxNoteUseCase(str(inbox_dir), str(template_path), sb_gateway)
    sb_service = SecondBrainService(
        register_inbox_note_usecase=register_inbox_uc,
        register_permanent_note_usecase=None,
        register_sense_making_note_usecase=None,
        search_notes_usecase=None,
        audit_zettelkasten_rules_usecase=None,
    )
    parser = MarkdownImageParser()
    attachments_dir = Path(sb_dir) / "90_Meta" / "Attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)

    process_uc = ProcessInboxItemUseCase(
        receiver=mobile_gateway,
        second_brain_service=sb_service,
        task_operations_service=test_context.task_operations_service,
        sb_gateway=sb_gateway,
        sb_attachments_dir=str(attachments_dir),
        parser=parser,
    )
    peek_uc = PeekInboxUseCase(mobile_gateway, parser)
    service = MobileVaultService(peek_uc, process_uc, None)
    return service, mobile_gateway, sb_gateway, inbox_dir, attachments_dir


def test_peek_inbox_read_only_integration(test_context: IntegrationTestContext):
    """
    [MV-RECV-01] PeekInboxUseCase: 未処理パケットと添付画像の参照（副作用なし）
    Vault内の未処理Inboxアイテムおよび添付画像の一覧が取得でき、
    実行後も原本ファイルが破壊されず残存することを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, _, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # テストデータの作成
        note1 = Path(mobile_dir) / "note1.md"
        note1.write_text("Note 1 with image\n![[image1.png]]", encoding="utf-8")
        img1 = Path(mobile_img_dir) / "image1.png"
        img1.write_text("fake binary data 1", encoding="utf-8")

        note2 = Path(mobile_dir) / "note2.md"
        note2.write_text("Note 2 text only", encoding="utf-8")

        # Peek 実行
        items = service.peek_inbox()
        assert len(items) == 2

        item_map = {item["item_id"]: item for item in items}
        assert "note1.md" in item_map
        assert "note2.md" in item_map

        assert item_map["note1.md"]["content"] == "Note 1 with image\n![[image1.png]]"
        assert len(item_map["note1.md"]["images"]) == 1
        assert item_map["note1.md"]["images"][0]["name"] == "image1.png"
        assert Path(item_map["note1.md"]["images"][0]["path"]).resolve() == img1.resolve()

        assert item_map["note2.md"]["content"] == "Note 2 text only"
        assert item_map["note2.md"]["images"] == []

        # Read-only 保証（原本ファイルが存在すること）
        assert note1.exists()
        assert note2.exists()
        assert img1.exists()


def test_process_inbox_lifecycle_idea_task_delete_integration(test_context: IntegrationTestContext):
    """
    [MV-RECV-02] ProcessInboxItemUseCase: idea/task/delete の振り分けとVault原本削除
    指定したInboxアイテムが idea / task / delete に応じて正しく振り分けられ、
    処理完了後にVaultから原本ファイルが自動削除されることを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, inbox_dir, attachments_dir = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 1. idea アクションの検証（Second Brain登録＋画像コピー＋原本削除）
        idea_path = Path(mobile_dir) / "idea_item.md"
        idea_path.write_text("Core idea\n![[idea_diagram.png]]", encoding="utf-8")
        idea_img = Path(mobile_img_dir) / "idea_diagram.png"
        idea_img.write_text("diagram content", encoding="utf-8")

        success_idea = service.process_inbox_item(
            item_id="idea_item.md", action="idea", title="Architectural Idea", tags=["concept/arch"]
        )
        assert success_idea is True
        assert not idea_path.exists()
        assert not idea_img.exists()

        created_notes = list(inbox_dir.glob("*.md"))
        assert len(created_notes) == 1
        assert "Architectural Idea" in created_notes[0].read_text(encoding="utf-8")
        assert (attachments_dir / "idea_diagram.png").exists()

        # 2. task アクションの検証（Task DB登録＋原本削除）
        task_path = Path(mobile_dir) / "task_item.md"
        task_path.write_text("Submit monthly report", encoding="utf-8")

        success_task = service.process_inbox_item(
            item_id="task_item.md", action="task", title="Monthly Report", energy_level="High"
        )
        assert success_task is True
        assert not task_path.exists()

        tasks = test_context.session.query(TaskModel).all()
        assert len(tasks) == 1
        assert tasks[0].title == "Monthly Report"
        assert tasks[0].category == TaskCategory.MUST.value

        # 3. delete アクションの検証（原本＋画像削除）
        del_path = Path(mobile_dir) / "delete_item.md"
        del_path.write_text("Trash note\n![[del_pic.png]]", encoding="utf-8")
        del_img = Path(mobile_img_dir) / "del_pic.png"
        del_img.write_text("trash pic", encoding="utf-8")

        success_del = service.process_inbox_item(item_id="delete_item.md", action="delete")
        assert success_del is True
        assert not del_path.exists()
        assert not del_img.exists()


def test_process_inbox_item_idempotency_integration(test_context: IntegrationTestContext):
    """
    [MV-IDEM-01] Idempotent Process Inbox Item: 二重実行時の安全性
    同一Inboxアイテムに対して二重に ProcessInboxItemUseCase が実行された場合、
    2回目は対象が存在しないため安全に False を返し、重複登録が発生しないことを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, inbox_dir, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 1. idea の二重実行検証
        note_path = Path(mobile_dir) / "idem_idea.md"
        note_path.write_text("Idempotent Idea Text", encoding="utf-8")

        res1 = service.process_inbox_item(item_id="idem_idea.md", action="idea", title="Unique Idea")
        assert res1 is True
        assert not note_path.exists()
        assert len(list(inbox_dir.glob("*.md"))) == 1

        res2 = service.process_inbox_item(item_id="idem_idea.md", action="idea", title="Unique Idea")
        assert res2 is False
        assert len(list(inbox_dir.glob("*.md"))) == 1

        # 2. task の二重実行検証
        task_path = Path(mobile_dir) / "idem_task.md"
        task_path.write_text("Idempotent Task Text", encoding="utf-8")

        res_task1 = service.process_inbox_item(item_id="idem_task.md", action="task", title="Unique Task")
        assert res_task1 is True
        assert not task_path.exists()
        tasks = test_context.session.query(TaskModel).all()
        assert len(tasks) == 1

        res_task2 = service.process_inbox_item(item_id="idem_task.md", action="task", title="Unique Task")
        assert res_task2 is False
        tasks_after = test_context.session.query(TaskModel).all()
        assert len(tasks_after) == 1


def test_peek_inbox_empty_vault_boundary_integration(test_context: IntegrationTestContext):
    """
    [MV-BOUND-01] Boundary: Inbox 0件時の空リスト返却
    Vault内に未処理Inboxアイテムが0件の場合、PeekInboxUseCase が空リスト [] を安全に返し
    例外が発生しないことを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, _, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        items = service.peek_inbox()
        assert items == []


def test_process_inbox_item_no_attachments_boundary_integration(test_context: IntegrationTestContext):
    """
    [MV-BOUND-02] Boundary: 添付画像0件メモの正常振り分け
    添付画像を含まないInboxアイテムに対して idea / task / delete が正常に完遂することを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, inbox_dir, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 1. idea without image
        idea_file = Path(mobile_dir) / "no_img_idea.md"
        idea_file.write_text("Pure text idea content", encoding="utf-8")
        res_idea = service.process_inbox_item(item_id="no_img_idea.md", action="idea", title="No Img Idea")
        assert res_idea is True
        assert not idea_file.exists()
        assert len(list(inbox_dir.glob("*.md"))) == 1

        # 2. task without image
        task_file = Path(mobile_dir) / "no_img_task.md"
        task_file.write_text("Pure text task content", encoding="utf-8")
        res_task = service.process_inbox_item(item_id="no_img_task.md", action="task", title="No Img Task")
        assert res_task is True
        assert not task_file.exists()
        tasks = test_context.session.query(TaskModel).all()
        assert len(tasks) == 1

        # 3. delete without image
        del_file = Path(mobile_dir) / "no_img_del.md"
        del_file.write_text("Pure text delete content", encoding="utf-8")
        res_del = service.process_inbox_item(item_id="no_img_del.md", action="delete")
        assert res_del is True
        assert not del_file.exists()


def test_process_inbox_item_empty_title_fallback_boundary_integration(test_context: IntegrationTestContext):
    """
    [MV-BOUND-03] Boundary: title空文字時のitem_idフォールバック
    title が空文字（""）の状態で ProcessInboxItemUseCase を実行した場合、
    item_id がフォールバックタイトルとして採用されることを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, inbox_dir, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 1. idea with empty title fallback
        idea_file = Path(mobile_dir) / "fallback_idea_note.md"
        idea_file.write_text("Memo content without explicit title", encoding="utf-8")
        res_idea = service.process_inbox_item(item_id="fallback_idea_note.md", action="idea", title="")
        assert res_idea is True
        assert not idea_file.exists()

        notes = list(inbox_dir.glob("*.md"))
        assert len(notes) == 1
        assert "fallback_idea_note.md" in notes[0].read_text(encoding="utf-8")

        # 2. task with empty title fallback
        task_file = Path(mobile_dir) / "fallback_task_note.md"
        task_file.write_text("Task description without explicit title", encoding="utf-8")
        res_task = service.process_inbox_item(item_id="fallback_task_note.md", action="task", title="")
        assert res_task is True
        assert not task_file.exists()

        tasks = test_context.session.query(TaskModel).all()
        assert len(tasks) == 1
        assert tasks[0].title == "fallback_task_note.md"


def test_process_inbox_item_mixed_image_formats_reconciliation_integration(test_context: IntegrationTestContext):
    """
    [MV-RECON-01] Reconciliation: ![[...]] と ![...](...) の複数混在リンク抽出とアセット移行
    Markdown本文中にObsidian形式と標準Markdown形式が混在している場合でも、
    すべての添付画像参照が抽出され、Second Brainへの移行およびVaultからの削除が行われることを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, _, attachments_dir = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 混在する画像リンクを持つMarkdownの作成
        mixed_content = (
            "# Mixed Notes\n"
            "WikiLink image: ![[wiki_shot.png]]\n"
            "Standard markdown image: ![Architecture Diagram](std_diag.jpg)\n"
            "Another WikiLink: ![[another_wiki.png]]\n"
        )
        note_file = Path(mobile_dir) / "mixed_format_note.md"
        note_file.write_text(mixed_content, encoding="utf-8")

        img1 = Path(mobile_img_dir) / "wiki_shot.png"
        img1.write_text("wiki_shot data", encoding="utf-8")
        img2 = Path(mobile_img_dir) / "std_diag.jpg"
        img2.write_text("std_diag data", encoding="utf-8")
        img3 = Path(mobile_img_dir) / "another_wiki.png"
        img3.write_text("another_wiki data", encoding="utf-8")

        # 実行
        res = service.process_inbox_item(item_id="mixed_format_note.md", action="idea", title="Mixed Formats")
        assert res is True

        # 原本ファイルの削除検証
        assert not note_file.exists()
        assert not img1.exists()
        assert not img2.exists()
        assert not img3.exists()

        # Second Brain側へのアセット移行検証
        assert (attachments_dir / "wiki_shot.png").exists()
        assert (attachments_dir / "std_diag.jpg").exists()
        assert (attachments_dir / "another_wiki.png").exists()


def test_process_inbox_item_invalid_action_fault_tolerance_integration(test_context: IntegrationTestContext):
    """
    [MV-FAULT-01] Fault Tolerance: 不正action時のValueError送出とファイル保全
    未知のアクションが指定された場合に ValueError が送出され、原本ファイルが保全されることを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, _, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        fault_note = Path(mobile_dir) / "fault_note.md"
        fault_note.write_text("Fault note with ![[preserve_pic.png]]", encoding="utf-8")
        fault_img = Path(mobile_img_dir) / "preserve_pic.png"
        fault_img.write_text("preserve content", encoding="utf-8")

        with pytest.raises(ValueError, match="Invalid action: unknown_action") as exc_info:
            service.process_inbox_item(item_id="fault_note.md", action="unknown_action")

        assert "Invalid action" in str(exc_info.value)
        # 異常系送出時は原本ファイル・画像が保持されること
        assert fault_note.exists()
        assert fault_img.exists()


def test_process_inbox_item_missing_image_fault_tolerance_integration(test_context: IntegrationTestContext):
    """
    [MV-FAULT-02] Fault Tolerance: 欠損画像があっても存在する画像のみ転送しメモ処理完遂
    Markdown本文中に画像参照が記述されているがVault上に実画像ファイルが存在しない場合（欠損時）、
    エラーで全体処理を中断せず、存在する画像のみコピーし、ノート登録と原本Markdown削除が安全に完遂することを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, inbox_dir, attachments_dir = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 存在する画像と欠損した画像への参照
        content = "Note referring to ![[existing.png]] and missing ![[ghost.png]]"
        note_file = Path(mobile_dir) / "partial_images.md"
        note_file.write_text(content, encoding="utf-8")

        existing_img = Path(mobile_img_dir) / "existing.png"
        existing_img.write_text("existing image data", encoding="utf-8")
        # ghost.png は作成しない（欠損状態）

        res = service.process_inbox_item(item_id="partial_images.md", action="idea", title="Partial Image Note")
        assert res is True

        # 原本ファイルおよび存在した画像が削除されること
        assert not note_file.exists()
        assert not existing_img.exists()

        # 存在する画像のみがSecond Brainへ移行されること
        assert (attachments_dir / "existing.png").exists()
        assert not (attachments_dir / "ghost.png").exists()

        # ノートが正常に作成されていること
        notes = list(inbox_dir.glob("*.md"))
        assert len(notes) == 1
        assert "Partial Image Note" in notes[0].read_text(encoding="utf-8")


def test_leave_no_trace_invariant_integration(test_context: IntegrationTestContext):
    """
    [MV-INVAR-01] Invariant: Leave No Trace - 処理後原本削除、異常時保全
    処理が成功したInboxアイテムおよび抽出画像はVault内に残留せず即時削除され、
    処理失敗・例外送出時には原本が保全されることを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, _, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        # 1. 正常処理後の完全削除（Leave No Trace）
        clean_note = Path(mobile_dir) / "clean_note.md"
        clean_note.write_text("Clean test\n![[clean_img.png]]", encoding="utf-8")
        clean_img = Path(mobile_img_dir) / "clean_img.png"
        clean_img.write_text("clean binary", encoding="utf-8")

        res = service.process_inbox_item(item_id="clean_note.md", action="idea", title="Clean Note")
        assert res is True
        assert len(list(Path(mobile_dir).glob("*.md"))) == 0
        assert len(list(Path(mobile_img_dir).glob("*"))) == 0

        # 2. 異常系発生時の原本保全（No Trace Cleanup が異常時には発動しないこと）
        err_note = Path(mobile_dir) / "err_note.md"
        err_note.write_text("Error note\n![[err_img.png]]", encoding="utf-8")
        err_img = Path(mobile_img_dir) / "err_img.png"
        err_img.write_text("error binary", encoding="utf-8")

        with pytest.raises(ValueError):
            service.process_inbox_item(item_id="err_note.md", action="invalid_action")

        assert err_note.exists()
        assert err_img.exists()


def test_peek_inbox_readonly_invariant_integration(test_context: IntegrationTestContext):
    """
    [MV-INVAR-02] Invariant: Peek実行時の状態非破壊保証（Read-only 保証）
    PeekInboxUseCase の実行前後でVault内のファイル内容および状態が一切変更されないことを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        service, _, _, _, _ = _create_harness(mobile_dir, mobile_img_dir, sb_dir, test_context)

        note_a = Path(mobile_dir) / "note_a.md"
        note_a_content = "# Title A\nSome body text\n![[asset_a.png]]"
        note_a.write_text(note_a_content, encoding="utf-8")

        img_a = Path(mobile_img_dir) / "asset_a.png"
        img_a_content = "raw binary data a"
        img_a.write_text(img_a_content, encoding="utf-8")

        # 1回目の Peek 実行
        items_1 = service.peek_inbox()
        assert len(items_1) == 1

        # 2回目の Peek 実行
        items_2 = service.peek_inbox()
        assert len(items_2) == 1

        # ファイル内容およびタイムスタンプ/存在の不変性を検証
        assert note_a.exists()
        assert note_a.read_text(encoding="utf-8") == note_a_content
        assert img_a.exists()
        assert img_a.read_text(encoding="utf-8") == img_a_content

        # Vault内に不要なテンポラリファイル等が増殖していないこと
        assert len(list(Path(mobile_dir).glob("*"))) == 1
        assert len(list(Path(mobile_img_dir).glob("*"))) == 1

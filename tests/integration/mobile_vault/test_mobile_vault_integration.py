"""[MV-RECV-01][MV-RECV-02][MV-RECV-03] Mobile Vault Integration Tests"""

import tempfile
from pathlib import Path

import pytest

from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.peek_inbox_usecase import PeekInboxUseCase
from application.mobile_vault.process_inbox_item_usecase import ProcessInboxItemUseCase
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.second_brain_service import SecondBrainService
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from infrastructure.local_file.local_file_second_brain_gateway import LocalFileSecondBrainGateway
from infrastructure.sqlalchemy.task_model import TaskModel
from tests.integration.conftest import IntegrationTestContext


def test_mobile_vault_inbox_lifecycle_integration(test_context: IntegrationTestContext):
    """
    [MV-RECV-01] PeekInboxUseCase: 未処理パケットと添付画像の参照（副作用なし）
    [MV-RECV-02] ProcessInboxItemUseCase: idea/task/delete の振り分けとVault原本削除
    実ファイルシステムとSQLite DBを貫通させ、Inboxパケットの受領から振り分け完了までのライフサイクルを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        # 1. Gateway & Service セットアップ
        mobile_gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, attachments_dir=mobile_img_dir)
        sb_gateway = LocalFileSecondBrainGateway(sb_dir)

        inbox_dir = Path(sb_dir) / "00_Inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        template_path = Path(sb_dir) / "template.md"
        template_path.write_text("# {{TITLE}}\n{{BODY}}\ntags: []")

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

        # 2. [MV-RECV-01] Peek の検証
        packet_path = Path(mobile_dir) / "item_test.md"
        packet_path.write_text("Test idea with image\n![[test_img.png]]")
        img_path = Path(mobile_img_dir) / "test_img.png"
        img_path.write_text("fake image content")

        inbox_items = service.peek_inbox()
        assert len(inbox_items) == 1
        assert inbox_items[0]["item_id"] == "item_test.md"
        assert inbox_items[0]["content"] == "Test idea with image\n![[test_img.png]]"
        assert len(inbox_items[0]["images"]) == 1
        assert inbox_items[0]["images"][0]["name"] == "test_img.png"

        # Peek は Read-only でありファイルが残っていることの確認
        assert img_path.exists()
        assert packet_path.exists()

        # 3. [MV-RECV-02] Process (idea アクション) の検証
        success_idea = service.process_inbox_item(
            item_id="item_test.md", action="idea", title="Great Idea", tags=["concept/test"]
        )
        assert success_idea is True
        # 原本ファイルが削除され、Second Brain側に移動・作成されたことを確認
        assert not img_path.exists()
        assert not packet_path.exists()
        idea_files = list(inbox_dir.glob("*.md"))
        assert len(idea_files) == 1
        assert "Great Idea" in idea_files[0].read_text()
        assert (attachments_dir / "test_img.png").exists()

        # 4. [MV-RECV-02] Process (task アクション) の検証
        item_task_path = Path(mobile_dir) / "item_task.md"
        item_task_path.write_text("Buy milk")

        success_task = service.process_inbox_item(
            item_id="item_task.md", action="task", title="Milk", energy_level="Low"
        )
        assert success_task is True
        assert not item_task_path.exists()

        # SQLite DBにタスクが永続化されたことを直接確認
        tasks = test_context.session.query(TaskModel).all()
        assert len(tasks) == 1
        assert tasks[0].title == "Milk"

        # 5. [MV-RECV-02] Process (delete アクション) の検証
        item_delete_path = Path(mobile_dir) / "item_delete.md"
        item_delete_path.write_text("Delete me with image\n![[del_img.png]]")
        del_img_path = Path(mobile_img_dir) / "del_img.png"
        del_img_path.write_text("image to be deleted")

        success_delete = service.process_inbox_item(item_id="item_delete.md", action="delete")
        assert success_delete is True
        assert not item_delete_path.exists()
        assert not del_img_path.exists()


def test_mobile_vault_invalid_action_integration(test_context: IntegrationTestContext):
    """
    [MV-RECV-03] 異常系: 無効なアクション指定時の例外送出
    想定外のアクション名が指定された場合にサイレントに完了せず ValueError が送出されることを検証する。
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        mobile_gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, attachments_dir=mobile_img_dir)
        sb_gateway = LocalFileSecondBrainGateway(sb_dir)
        parser = MarkdownImageParser()

        process_uc = ProcessInboxItemUseCase(
            receiver=mobile_gateway,
            second_brain_service=None,
            task_operations_service=test_context.task_operations_service,
            sb_gateway=sb_gateway,
            sb_attachments_dir=sb_dir,
            parser=parser,
        )
        service = MobileVaultService(None, process_uc, None)

        item_invalid_path = Path(mobile_dir) / "item_invalid.md"
        item_invalid_path.write_text("Invalid action note")

        with pytest.raises(ValueError, match="Invalid action: invalid_action") as exc_info:
            service.process_inbox_item(item_id="item_invalid.md", action="invalid_action")

        assert "Invalid action" in str(exc_info.value)
        # 異常系ではファイルが勝手に消えていないことを確認
        assert item_invalid_path.exists()

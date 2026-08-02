"""[MV-RECV-01][MV-RECV-02][MV-RECV-03] Mobile Vault Integration Tests"""

import tempfile
from pathlib import Path

from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.peek_inbox_usecase import PeekInboxUseCase
from application.mobile_vault.process_inbox_item_usecase import ProcessInboxItemUseCase
from application.second_brain.second_brain_service import SecondBrainService
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from infrastructure.local_file.local_file_second_brain_gateway import LocalFileSecondBrainGateway
from tests.integration.conftest import IntegrationTestContext


def test_peek_and_process_inbox_item_integration(test_context: IntegrationTestContext):
    """
    [MV-RECV-01] PeekInboxUseCase
    [MV-RECV-02] ProcessInboxItemUseCase
    [MV-RECV-03] ProcessInboxItemUseCase with invalid action
    DBまで貫通させ、実際のファイル移動・タスク生成が行われるか検証する
    """
    with (
        tempfile.TemporaryDirectory() as mobile_dir,
        tempfile.TemporaryDirectory() as mobile_img_dir,
        tempfile.TemporaryDirectory() as sb_dir,
    ):
        # Gatewayの初期化
        mobile_gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, attachments_dir=mobile_img_dir)
        sb_gateway = LocalFileSecondBrainGateway(sb_dir)

        # SecondBrain側のテストデータとUseCaseの準備
        inbox_dir = Path(sb_dir) / "00_Inbox"
        inbox_dir.mkdir(parents=True, exist_ok=True)
        template_path = Path(sb_dir) / "template.md"
        template_path.write_text("# {{TITLE}}\n{{BODY}}\ntags: []")

        from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase

        register_inbox_uc = RegisterInboxNoteUseCase(str(inbox_dir), str(template_path), sb_gateway)

        sb_service = SecondBrainService(
            register_inbox_note_usecase=register_inbox_uc,
            register_permanent_note_usecase=None,
            register_sense_making_note_usecase=None,
            search_notes_usecase=None,
            audit_zettelkasten_rules_usecase=None,
        )
        parser = MarkdownImageParser()

        # テストデータの準備 (Mobile側)
        packet_path = Path(mobile_dir) / "item_test.md"
        packet_path.write_text("Test idea with image\n![[test_img.png]]")
        img_path = Path(mobile_img_dir) / "test_img.png"
        img_path.write_text("fake image content")

        # UseCase初期化
        peek_uc = PeekInboxUseCase(mobile_gateway, parser)
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
        service = MobileVaultService(peek_uc, process_uc, None)

        # --- 1. Peekのテスト [MV-RECV-01] ---
        inbox_items = service.peek_inbox()
        assert len(inbox_items) == 1
        assert inbox_items[0]["item_id"] == "item_test.md"
        assert inbox_items[0]["content"] == "Test idea with image\n![[test_img.png]]"
        assert len(inbox_items[0]["images"]) == 1
        assert inbox_items[0]["images"][0]["name"] == "test_img.png"

        # ファイルがまだ削除・移動されていないことの確認
        assert img_path.exists()
        assert packet_path.exists()

        # --- 2. Processのテスト (ideaアクション) [MV-RECV-02] ---
        # "idea" アクションは、second-brain の 00_Inbox に保存され、画像が 90_Meta/Attachments に移動する
        success = service.process_inbox_item(
            item_id="item_test.md", action="idea", title="Great Idea", tags=["concept/test"]
        )
        assert success is True

        # 副作用の検証1: モバイル側のファイルが消えたか
        assert not img_path.exists()
        assert not packet_path.exists()

        # 副作用の検証2: SecondBrain側にファイルが作成されたか
        inbox_dir = Path(sb_dir) / "00_Inbox"
        attachments_dir = Path(sb_dir) / "90_Meta" / "Attachments"

        # Ideaノートの確認
        idea_files = list(inbox_dir.glob("*.md"))
        assert len(idea_files) == 1
        assert "Great Idea" in idea_files[0].read_text()

        # 画像が移動したかの確認
        assert (attachments_dir / "test_img.png").exists()

        # --- 3. Processのテスト (taskアクション) [MV-RECV-02] ---
        # もう一つテストデータを作成
        item_task_path = Path(mobile_dir) / "item_task.md"
        item_task_path.write_text("Buy milk")

        success_task = service.process_inbox_item(
            item_id="item_task.md", action="task", title="Milk", energy_level="Low"
        )
        assert success_task is True

        # DBにタスクが登録されたかを直接アサーション (Integration Testの責務)
        from infrastructure.sqlalchemy.task_model import TaskModel

        tasks = test_context.session.query(TaskModel).all()
        assert len(tasks) == 1
        assert tasks[0].title == "Milk"
        # モバイル側のファイル削除確認
        assert not item_task_path.exists()

        # --- 4. Processのテスト (deleteアクション) [MV-RECV-02] ---
        item_delete_path = Path(mobile_dir) / "item_delete.md"
        item_delete_path.write_text("Delete me with image\n![[del_img.png]]")
        del_img_path = Path(mobile_img_dir) / "del_img.png"
        del_img_path.write_text("image to be deleted")

        success_delete = service.process_inbox_item(item_id="item_delete.md", action="delete")
        assert success_delete is True
        assert not item_delete_path.exists()
        assert not del_img_path.exists()

        # --- 5. 異常系テスト (無効なアクション) [MV-RECV-03] ---
        item_invalid_path = Path(mobile_dir) / "item_invalid.md"
        item_invalid_path.write_text("Invalid action note")

        import pytest

        with pytest.raises(ValueError, match="Invalid action: invalid_action"):
            service.process_inbox_item(item_id="item_invalid.md", action="invalid_action")

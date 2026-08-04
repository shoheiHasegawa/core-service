from unittest.mock import MagicMock

import pytest

from application.mobile_vault.process_inbox_item_usecase import ProcessInboxItemUseCase
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.task_operations_service import TaskOperationsService
from domain.mobile_vault.inbox_item import InboxItem
from domain.mobile_vault.inbox_receiver import InboxReceiver
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.second_brain.repository import SecondBrainGateway
from domain.task_management.task import TaskCategory


def _create_usecase(
    receiver=None,
    sb_service=None,
    task_service=None,
    sb_gateway=None,
    sb_attachments_dir="/fake/attachments",
    parser=None,
):
    return ProcessInboxItemUseCase(
        receiver=receiver or MagicMock(spec=InboxReceiver),
        second_brain_service=sb_service or MagicMock(spec=SecondBrainService),
        task_operations_service=task_service or MagicMock(spec=TaskOperationsService),
        sb_gateway=sb_gateway or MagicMock(spec=SecondBrainGateway),
        sb_attachments_dir=sb_attachments_dir,
        parser=parser or MagicMock(spec=MarkdownImageParser),
    )


def test_process_inbox_item_idea_with_images():
    """[MV-RECV-02] Process Mobile PacketのIdea登録処理および画像コピー・削除のテスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_sb_gateway = MagicMock(spec=SecondBrainGateway)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="test_idea.md", content="Idea body ![[img1.png]]", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = ["img1.png"]
    mock_receiver.get_image_path.return_value = "/vault/attachments/img1.png"

    usecase = _create_usecase(
        receiver=mock_receiver,
        sb_service=mock_sb_service,
        task_service=mock_task_service,
        sb_gateway=mock_sb_gateway,
        sb_attachments_dir="/second_brain/attachments",
        parser=mock_parser,
    )

    result = usecase.execute(item_id="test_idea.md", action="idea", title="My Idea", tags=["tag1"])

    assert result is True
    mock_sb_service.register_inbox_note.assert_called_once()
    dto = mock_sb_service.register_inbox_note.call_args[0][0]
    assert dto.title == "My Idea"
    assert dto.content == "Idea body ![[img1.png]]"
    assert dto.tags == ["tag1"]

    mock_receiver.get_image_path.assert_called_once_with("img1.png")
    mock_sb_gateway.copy_asset.assert_called_once_with(
        "/vault/attachments/img1.png", "/second_brain/attachments/img1.png"
    )
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_receiver.delete_image.assert_called_once_with("img1.png")
    mock_task_service.register_task.assert_not_called()


def test_process_inbox_item_idea_fallback_title_and_no_images():
    """[MV-BOUND-02] [MV-BOUND-03] title空文字時のitem_idフォールバックおよび画像0件テスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_sb_gateway = MagicMock(spec=SecondBrainGateway)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="note_123.md", content="Idea body without images", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = []

    usecase = _create_usecase(
        receiver=mock_receiver,
        sb_service=mock_sb_service,
        task_service=mock_task_service,
        sb_gateway=mock_sb_gateway,
        parser=mock_parser,
    )

    result = usecase.execute(item_id="note_123.md", action="idea", title="")

    assert result is True
    mock_sb_service.register_inbox_note.assert_called_once()
    dto = mock_sb_service.register_inbox_note.call_args[0][0]
    assert dto.title == "note_123.md"
    assert dto.content == "Idea body without images"
    assert dto.tags is None

    mock_sb_gateway.copy_asset.assert_not_called()
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_receiver.delete_image.assert_not_called()


def test_process_inbox_item_idea_missing_image_path():
    """[MV-FAULT-02] 画像欠損時（get_image_pathがNone）の安全な継続テスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_sb_gateway = MagicMock(spec=SecondBrainGateway)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="missing_img.md", content="Body with missing img", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = ["missing.png"]
    mock_receiver.get_image_path.return_value = None

    usecase = _create_usecase(
        receiver=mock_receiver,
        sb_service=mock_sb_service,
        sb_gateway=mock_sb_gateway,
        parser=mock_parser,
    )

    result = usecase.execute(item_id="missing_img.md", action="idea")

    assert result is True
    mock_sb_gateway.copy_asset.assert_not_called()
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_receiver.delete_image.assert_called_once_with("missing.png")


def test_process_inbox_item_task_high_energy():
    """[MV-RECV-02] Task登録処理（High Energy -> MUST）のテスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="test_task.md", content="Task body", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = []

    usecase = _create_usecase(
        receiver=mock_receiver,
        sb_service=mock_sb_service,
        task_service=mock_task_service,
        parser=mock_parser,
    )

    result = usecase.execute(item_id="test_task.md", action="task", title="My Task", energy_level="High")

    assert result is True
    mock_task_service.register_task.assert_called_once_with(
        title="My Task", description="Task body", category=TaskCategory.MUST, estimated_minutes=30
    )
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_sb_service.register_inbox_note.assert_not_called()


def test_process_inbox_item_task_fallback_title_and_low_energy_with_images():
    """[MV-RECV-02] [MV-BOUND-03] Task登録処理（title空文字フォールバック & Low Energy -> SHOULD & 画像削除）のテスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="task_fallback.md", content="Task with image", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = ["task_img.png"]

    usecase = _create_usecase(
        receiver=mock_receiver,
        task_service=mock_task_service,
        parser=mock_parser,
    )

    result = usecase.execute(item_id="task_fallback.md", action="task", title="", energy_level="Low")

    assert result is True
    mock_task_service.register_task.assert_called_once_with(
        title="task_fallback.md", description="Task with image", category=TaskCategory.SHOULD, estimated_minutes=30
    )
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_receiver.delete_image.assert_called_once_with("task_img.png")


def test_process_inbox_item_delete_with_images():
    """[MV-RECV-02] Delete処理および添付画像削除のテスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="test_delete.md", content="Delete body", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = ["img_del.png"]

    usecase = _create_usecase(
        receiver=mock_receiver,
        sb_service=mock_sb_service,
        task_service=mock_task_service,
        parser=mock_parser,
    )

    result = usecase.execute(item_id="test_delete.md", action="delete")

    assert result is True
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_receiver.delete_image.assert_called_once_with("img_del.png")
    mock_sb_service.register_inbox_note.assert_not_called()
    mock_task_service.register_task.assert_not_called()


def test_process_inbox_item_cleanup_images_value_error_ignored():
    """[MV-FAULT-02] 画像削除時のValueError例外が安全に無視されることのテスト。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="del_err.md", content="Content", images=[])
    mock_receiver.get_item.return_value = mock_packet
    mock_parser.extract_images.return_value = ["img_err.png"]
    mock_receiver.delete_image.side_effect = ValueError("File does not exist")

    usecase = _create_usecase(
        receiver=mock_receiver,
        parser=mock_parser,
    )

    result = usecase.execute(item_id="del_err.md", action="delete")

    assert result is True
    mock_receiver.delete_item.assert_called_once_with(mock_packet)
    mock_receiver.delete_image.assert_called_once_with("img_err.png")


def test_process_inbox_item_not_found():
    """[MV-IDEM-01] 対象パケットが存在しない場合は False を返す。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_receiver.get_item.return_value = None

    usecase = _create_usecase(receiver=mock_receiver)

    result = usecase.execute(item_id="non_existent.md", action="idea")
    assert result is False


def test_process_inbox_item_invalid_action():
    """[MV-FAULT-01] 無効なアクションが指定された場合は ValueError を送出する。"""
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_packet = InboxItem(item_id="test.md", content="Body", images=[])
    mock_receiver.get_item.return_value = mock_packet

    usecase = _create_usecase(receiver=mock_receiver)

    with pytest.raises(ValueError, match="Invalid action: invalid_action") as exc_info:
        usecase.execute(item_id="test.md", action="invalid_action")
    assert "Invalid action" in str(exc_info.value)

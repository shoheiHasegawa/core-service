from unittest.mock import MagicMock

from application.mobile_vault.process_mobile_packet_usecase import ProcessMobilePacketUseCase
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.task_operations_service import TaskOperationsService
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.mobile_vault.packet import Packet
from domain.mobile_vault.packet_receiver import PacketReceiver
from domain.second_brain.repository import SecondBrainGateway
from domain.task_management.task import TaskCategory


def test_process_mobile_packet_idea():
    """[MV-RECV-02] Process Mobile PacketのIdea登録処理のテスト。"""
    mock_receiver = MagicMock(spec=PacketReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_sb_gateway = MagicMock(spec=SecondBrainGateway)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = Packet(packet_id="test_idea.md", content="Idea body", images=[])
    mock_receiver.get_packet.return_value = mock_packet
    mock_parser.extract_images.return_value = []

    usecase = ProcessMobilePacketUseCase(
        receiver=mock_receiver,
        second_brain_service=mock_sb_service,
        task_operations_service=mock_task_service,
        sb_gateway=mock_sb_gateway,
        sb_attachments_dir="/fake/attachments",
        parser=mock_parser,
    )

    result = usecase.execute(packet_id="test_idea.md", action="idea", title="My Idea", tags=["tag1"])

    assert result is True
    mock_sb_service.register_inbox_note.assert_called_once()
    dto = mock_sb_service.register_inbox_note.call_args[0][0]
    assert dto.title == "My Idea"
    assert dto.content == "Idea body"
    assert dto.tags == ["tag1"]

    mock_receiver.delete_packet.assert_called_once_with(mock_packet)
    mock_task_service.register_task.assert_not_called()


def test_process_mobile_packet_task():
    """[MV-RECV-02] Process Mobile PacketのTask登録処理のテスト。"""
    mock_receiver = MagicMock(spec=PacketReceiver)
    mock_sb_service = MagicMock(spec=SecondBrainService)
    mock_task_service = MagicMock(spec=TaskOperationsService)
    mock_sb_gateway = MagicMock(spec=SecondBrainGateway)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = Packet(packet_id="test_task.md", content="Task body", images=[])
    mock_receiver.get_packet.return_value = mock_packet
    mock_parser.extract_images.return_value = []

    usecase = ProcessMobilePacketUseCase(
        receiver=mock_receiver,
        second_brain_service=mock_sb_service,
        task_operations_service=mock_task_service,
        sb_gateway=mock_sb_gateway,
        sb_attachments_dir="/fake/attachments",
        parser=mock_parser,
    )

    result = usecase.execute(packet_id="test_task.md", action="task", title="My Task", energy_level="High")

    assert result is True
    mock_task_service.register_task.assert_called_once_with(
        title="My Task", description="Task body", category=TaskCategory.MUST, estimated_minutes=30
    )
    mock_receiver.delete_packet.assert_called_once_with(mock_packet)
    mock_sb_service.register_inbox_note.assert_not_called()

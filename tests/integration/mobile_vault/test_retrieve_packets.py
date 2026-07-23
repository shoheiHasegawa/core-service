from integration.conftest import IntegrationTestContext
from sqlalchemy import text

# Import the NEW classes (these will fail until implemented)
from application.mobile_vault.retrieve_packets_usecase import RetrievePacketsUseCase
from domain.mobile_vault.gateway import PacketReceiver
from domain.mobile_vault.packet import Packet
from domain.mobile_vault.parser import MarkdownImageParser


class FakePacketReceiver(PacketReceiver):
    def __init__(self):
        self.packets = [Packet(packet_id="test-1", content="Test Packet", images=[])]
        self.deleted_ids = []

    def fetch_unprocessed_packets(self) -> list[Packet]:
        return self.packets

    def delete_packet(self, packet: Packet) -> None:
        self.deleted_ids.append(packet.packet_id)


def test_retrieve_packets(test_context: IntegrationTestContext):
    """
    [MV-RETRIEVE-01] Retrieve Unprocessed Packets (未処理パケットの回収)
    """
    # Arrange
    receiver = FakePacketReceiver()
    parser = MarkdownImageParser()
    use_case = RetrievePacketsUseCase(receiver=receiver, parser=parser, task_repository=test_context.task_repo)

    # Act
    count = use_case.execute()

    # Assert
    assert count == 1
    assert "test-1" in receiver.deleted_ids

    # Verify task generation in DB
    stmt = text("SELECT count(*) FROM tasks WHERE title = 'Process Packet: test-1'")
    result = test_context.session.execute(stmt).scalar()
    assert result == 1

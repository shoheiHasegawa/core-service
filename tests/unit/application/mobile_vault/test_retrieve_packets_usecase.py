from unittest.mock import MagicMock

from application.mobile_vault.retrieve_packets_usecase import RetrievePacketsUseCase
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.mobile_vault.packet_receiver import PacketReceiver
from domain.task_management.task_repository import TaskRepository


def test_retrieve_packets():
    """[MV-RETRIEVE-01]"""
    receiver = MagicMock(spec=PacketReceiver)
    parser = MagicMock(spec=MarkdownImageParser)
    task_repo = MagicMock(spec=TaskRepository)

    receiver.fetch_unprocessed_packets.return_value = []
    usecase = RetrievePacketsUseCase(receiver, parser, task_repo)

    results = usecase.execute()

    assert results == 0
    receiver.fetch_unprocessed_packets.assert_called_once()

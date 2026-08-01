from unittest.mock import MagicMock

from application.mobile_vault.peek_inbox_usecase import PeekInboxUseCase
from domain.mobile_vault.inbox_item import InboxItem
from domain.mobile_vault.inbox_receiver import InboxReceiver
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser


def test_peek_inbox_returns_packets():
    """[MV-RECV-01] Peek Mobile Inbox の正常系テスト。"""
    # Arrange
    mock_receiver = MagicMock(spec=InboxReceiver)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_packet = InboxItem(item_id="test1.md", content="Hello\n![[img.png]]", images=[])
    mock_receiver.fetch_unprocessed_items.return_value = [mock_packet]
    mock_parser.extract_images.return_value = ["img.png"]
    mock_receiver.get_image_path.return_value = "/fake/img.png"

    usecase = PeekInboxUseCase(receiver=mock_receiver, parser=mock_parser)

    # Act
    result = usecase.execute()

    # Assert
    assert len(result) == 1
    assert result[0]["item_id"] == "test1.md"
    assert result[0]["content"] == "Hello\n![[img.png]]"
    assert len(result[0]["images"]) == 1
    assert result[0]["images"][0]["name"] == "img.png"
    assert result[0]["images"][0]["path"] == "/fake/img.png"

    mock_receiver.fetch_unprocessed_items.assert_called_once()
    mock_parser.extract_images.assert_called_once_with("Hello\n![[img.png]]")
    mock_receiver.get_image_path.assert_called_once_with("img.png")

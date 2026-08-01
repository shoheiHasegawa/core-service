from domain.mobile_vault.inbox_item import InboxItem


def test_packet_generation_assigns_unique_id():
    """[MV-RECV-01]"""
    """[MV-RECV-01]
    Packetエンティティ生成時、インフラ層に依存せず一意のIDが採番されることのテスト。
    """
    content = "Some note content"
    images = ["test.png"]

    packet1 = InboxItem.create(content=content, images=images)
    packet2 = InboxItem.create(content=content, images=images)

    assert packet1.item_id is not None
    assert packet2.item_id is not None
    assert packet1.item_id != packet2.item_id

    assert packet1.content == content
    assert packet1.images == images

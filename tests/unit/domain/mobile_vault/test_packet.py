from domain.mobile_vault.packet import Packet


def test_packet_generation_assigns_unique_id():
    """[MV-RECV-01]"""
    """[MV-RECV-01]
    Packetエンティティ生成時、インフラ層に依存せず一意のIDが採番されることのテスト。
    """
    content = "Some note content"
    images = ["test.png"]

    packet1 = Packet.create(content=content, images=images)
    packet2 = Packet.create(content=content, images=images)

    assert packet1.packet_id is not None
    assert packet2.packet_id is not None
    assert packet1.packet_id != packet2.packet_id

    assert packet1.content == content
    assert packet1.images == images

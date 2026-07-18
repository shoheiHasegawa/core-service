# 未実装のため ImportError (Red) になる
from domain.mobile_vault.packet import Packet
from domain.mobile_vault.parser import MarkdownImageParser


def test_markdown_image_parser_extracts_images():
    """[SCENARIO-01]"""
    """[SCENARIO-01]
    MarkdownImageParserがMarkdown文字列から画像リンク（Obsidian形式や標準MD形式）を抽出するテスト。
    """
    parser = MarkdownImageParser()
    content = "Here is an image: ![[test_image.png]] and another ![alt text](sample.jpg)"

    images = parser.extract_images(content)

    assert len(images) == 2
    assert "test_image.png" in images
    assert "sample.jpg" in images


def test_packet_generation_assigns_unique_id():
    """[SCENARIO-01]"""
    """[SCENARIO-01]
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

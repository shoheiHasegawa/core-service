from domain.mobile_vault.markdown_image_parser import MarkdownImageParser


def test_markdown_image_parser_extracts_images():
    """[MV-RECV-01]
    MarkdownImageParserがMarkdown文字列から画像リンク（Obsidian形式や標準MD形式）を抽出するテスト。
    """
    parser = MarkdownImageParser()
    content = "Here is an image: ![[test_image.png]] and another ![alt text](sample.jpg)"

    images = parser.extract_images(content)

    assert len(images) == 2
    assert "test_image.png" in images
    assert "sample.jpg" in images

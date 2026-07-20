import unittest

from infrastructure.markdown_parser import MarkdownParser


class TestMarkdownParser(unittest.TestCase):
    def test_parse_frontmatter_keys_no_match(self):
        """[MV-FILE-01]"""
        """[MV-FILE-04] Frontmatterがない場合のキー抽出"""
        content = "# No frontmatter here\nJust text."
        parser = MarkdownParser(content)
        keys = parser.parse_frontmatter_keys()
        assert len(keys) == 0

    def test_parse_frontmatter_keys_invalid_format(self):
        """[MV-FILE-01]"""
        """[MV-FILE-05] 不正なFrontmatterフォーマット時の耐性"""
        content = "---\njust some text without colon\n---\n"
        parser = MarkdownParser(content)
        keys = parser.parse_frontmatter_keys()
        assert len(keys) == 0

    def test_extract_tags_and_aliases_valid(self):
        """[MV-FILE-01]"""
        """[MV-FILE-06] TagsとAliasesの抽出"""
        content = """---
tags: [#test]
aliases: [TestAlias]
other: value
---
"""
        parser = MarkdownParser(content)
        tags, aliases = parser.extract_tags_and_aliases()
        assert len(tags) == 1
        assert "tags: [#test]" in tags[0]
        assert len(aliases) == 1
        assert "aliases: [TestAlias]" in aliases[0]

    def test_extract_tags_and_aliases_no_frontmatter(self):
        """[MV-FILE-01]"""
        """[MV-FILE-07] Frontmatterがない場合のTags抽出エッジケース"""
        content = "tags: [#test]\nBut not in frontmatter!"
        parser = MarkdownParser(content)
        tags, aliases = parser.extract_tags_and_aliases()
        assert len(tags) == 0
        assert len(aliases) == 0


if __name__ == "__main__":
    unittest.main()

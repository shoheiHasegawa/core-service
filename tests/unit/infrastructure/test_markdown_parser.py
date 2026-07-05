import unittest

from infrastructure.markdown_parser import MarkdownParser


class TestMarkdownParser(unittest.TestCase):
    def test_parse_frontmatter_keys_no_match(self):
        """[SCENARIO-04] Frontmatterがない場合のキー抽出"""
        content = "# No frontmatter here\nJust text."
        parser = MarkdownParser(content)
        keys = parser.parse_frontmatter_keys()
        self.assertEqual(len(keys), 0)

    def test_parse_frontmatter_keys_invalid_format(self):
        """[SCENARIO-05] 不正なFrontmatterフォーマット時の耐性"""
        content = "---\njust some text without colon\n---\n"
        parser = MarkdownParser(content)
        keys = parser.parse_frontmatter_keys()
        self.assertEqual(len(keys), 0)

    def test_extract_tags_and_aliases_valid(self):
        """[SCENARIO-06] TagsとAliasesの抽出"""
        content = """---
tags: [#test]
aliases: [TestAlias]
other: value
---
"""
        parser = MarkdownParser(content)
        tags, aliases = parser.extract_tags_and_aliases()
        self.assertEqual(len(tags), 1)
        self.assertIn("tags: [#test]", tags[0])
        self.assertEqual(len(aliases), 1)
        self.assertIn("aliases: [TestAlias]", aliases[0])

    def test_extract_tags_and_aliases_no_frontmatter(self):
        """[SCENARIO-07] Frontmatterがない場合のTags抽出エッジケース"""
        content = "tags: [#test]\nBut not in frontmatter!"
        parser = MarkdownParser(content)
        tags, aliases = parser.extract_tags_and_aliases()
        self.assertEqual(len(tags), 0)
        self.assertEqual(len(aliases), 0)


if __name__ == "__main__":
    unittest.main()

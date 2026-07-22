import unittest

from infrastructure.markdown_parser import MarkdownParser


class TestMarkdownParser(unittest.TestCase):
    def test_parse_frontmatter_keys_no_match(self):
        """[MV-RETRIEVE-01]"""
        """[MV-FILE-04] Frontmatterがない場合のキー抽出"""
        content = "# No frontmatter here\nJust text."
        parser = MarkdownParser(content)
        keys = parser.parse_frontmatter_keys()
        assert len(keys) == 0

    def test_parse_frontmatter_keys_invalid_format(self):
        """[MV-RETRIEVE-01]"""
        """[MV-FILE-05] 不正なFrontmatterフォーマット時の耐性"""
        content = "---\njust some text without colon\n---\n"
        parser = MarkdownParser(content)
        keys = parser.parse_frontmatter_keys()
        assert len(keys) == 0

    def test_extract_tags_and_aliases_valid(self):
        """[MV-RETRIEVE-01]"""
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
        """[MV-RETRIEVE-01]"""
        """[MV-FILE-07] Frontmatterがない場合のTags抽出エッジケース"""
        content = "tags: [#test]\nBut not in frontmatter!"
        parser = MarkdownParser(content)
        tags, aliases = parser.extract_tags_and_aliases()
        assert len(tags) == 0
        assert len(aliases) == 0


class TestBriefingMarkdownParser(unittest.TestCase):
    def test_parse_completed_task_ids(self):
        """[TM-SYNC-04] Markdownから完了済みタスクのIDを抽出する"""
        from domain.mobile_vault.parser import BriefingMarkdownParser

        content = """# Daily Briefing (2026-07-22)

## 🎯 Scheduled Tasks
- [x] Task 1 (予定: 30m) <!-- id: t1 -->
- [ ] Task 2 (予定: 60m) <!-- id: t2 -->
- [x] Task 3 (予定: 15m) <!-- id: t3 -->
- [x] Normal completed item without id
"""
        parser = BriefingMarkdownParser()
        completed_ids = parser.parse_completed_task_ids(content)

        assert completed_ids == ["t1", "t3"]


if __name__ == "__main__":
    unittest.main()

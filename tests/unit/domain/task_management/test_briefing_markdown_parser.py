import unittest

from domain.task_management.briefing_markdown_parser import BriefingMarkdownParser


class TestBriefingMarkdownParser(unittest.TestCase):
    def test_parse_completed_task_ids(self):
        """[TM-SYNC-04] Markdownから完了済みタスクのIDを抽出する"""
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

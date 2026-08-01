import unittest
from datetime import date

from domain.task_management.briefing_markdown_parser import BriefingMarkdownParser


class TestBriefingMarkdownParser(unittest.TestCase):
    def setUp(self):
        self.parser = BriefingMarkdownParser()

    def test_parse_worklogs_single_completed(self):
        """[TM-SYNC-04] 基本的な完了タスクのパースができること"""
        content = "- [x] 散歩 (予定: 30m) <!-- id: t1 -->"
        target_date = date(2026, 7, 18)
        worklogs = self.parser.parse_worklogs(content, target_date)

        assert len(worklogs) == 1
        assert worklogs[0].task_id == "t1"
        assert worklogs[0].is_completed is True
        assert worklogs[0].actual_minutes is None
        assert worklogs[0].target_date == date(2026, 7, 18)

    def test_parse_worklogs_with_actual_minutes(self):
        """[TM-SYNC-04] 実績分数が指定されている場合に正しくパースできること"""
        content = "- [ ] ランニング (予定: 60m) <!-- id: t2 --> 45"
        target_date = date(2026, 7, 18)
        worklogs = self.parser.parse_worklogs(content, target_date)

        assert len(worklogs) == 1
        assert worklogs[0].task_id == "t2"
        assert worklogs[0].is_completed is False
        assert worklogs[0].actual_minutes == 45
        assert worklogs[0].target_date == date(2026, 7, 18)

    def test_parse_worklogs_with_memo(self):
        """[TM-SYNC-04] タスク下のメモを正しく抽出できること"""
        content = """- [ ] 読書 (予定: 30m) <!-- id: t3 --> 20
  メモ: 1章まで読んだ
"""
        target_date = date(2026, 7, 19)
        worklogs = self.parser.parse_worklogs(content, target_date)

        assert len(worklogs) == 1
        assert worklogs[0].task_id == "t3"
        assert worklogs[0].is_completed is False
        assert worklogs[0].actual_minutes == 20
        assert worklogs[0].memo == "1章まで読んだ"
        assert worklogs[0].target_date == date(2026, 7, 19)

    def test_parse_worklogs_mixed(self):
        """[TM-SYNC-04] 複数タスクとメモが混在するケースでも正しくパースできること"""
        content = """- [x] Task A <!-- id: ta --> 30
  メモ: Done!
- [ ] Task B <!-- id: tb -->
  メモ: Pending
"""
        target_date = date(2026, 7, 20)
        worklogs = self.parser.parse_worklogs(content, target_date)

        assert len(worklogs) == 2
        assert worklogs[0].task_id == "ta"
        assert worklogs[0].is_completed is True
        assert worklogs[0].actual_minutes == 30
        assert worklogs[0].memo == "Done!"
        assert worklogs[0].target_date == date(2026, 7, 20)

        assert worklogs[1].task_id == "tb"
        assert worklogs[1].is_completed is False
        assert worklogs[1].actual_minutes is None
        assert worklogs[1].memo == "Pending"
        assert worklogs[1].target_date == date(2026, 7, 20)


if __name__ == "__main__":
    unittest.main()

from datetime import date

from domain.task_management.briefing_formatter import BriefingMarkdownFormatter
from domain.task_management.task import DailyBriefing, Task, WarningFlag


def test_briefing_markdown_formatter_format():
    """[TM-SYNC-03] BriefingMarkdownFormatter.format の検証 (Red)"""
    target_date = date(2026, 7, 22)
    task1 = Task(id="t1", title="Test Task 1", category="M", estimated_minutes=30)
    task2 = Task(id="t2", title="Test Task 2", category="S", estimated_minutes=60, last_memo="Carry over")
    briefing = DailyBriefing(
        target_date=target_date,
        scheduled_tasks=[task1, task2],
        deferred_tasks=[],
        warning_flags=[WarningFlag.W_RATIO_LOW],
    )

    formatter = BriefingMarkdownFormatter()
    content = formatter.format(briefing)

    assert "# Daily Briefing (2026-07-22)" in content
    assert "## ⚠️ Warnings" in content
    assert "- W_RATIO_LOW" in content
    assert "- [ ] Test Task 1 (予定: 30m) <!-- id: t1 -->" in content
    assert "- [ ] Test Task 2 (予定: 60m) <!-- id: t2 -->" in content
    assert "前回メモ: Carry over" in content

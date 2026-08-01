from domain.task_management.task import DailyBriefing


class BriefingMarkdownFormatter:
    def format(self, briefing: DailyBriefing) -> str:
        target_date = briefing.target_date
        lines = [f"# Daily Briefing ({target_date.strftime('%Y-%m-%d')})\n"]

        if briefing.warning_flags:
            lines.append("## ⚠️ Warnings")
            for w in briefing.warning_flags:
                lines.append(f"- {w.value}")
            lines.append("")

        lines.append("## Today's Tasks")
        for t in briefing.scheduled_tasks:
            lines.append(f"- [ ] {t.title} (予定: {t.estimated_minutes}m) <!-- id: {t.id} -->")
            if getattr(t, "last_memo", None):
                lines.append(f"  前回メモ: {t.last_memo}")
            lines.append("  実績: <!-- 例: 45m -->")
            lines.append("  メモ: <!-- 作業中の気づきや次にやること等を記入 -->")

        return "\n".join(lines) + "\n"

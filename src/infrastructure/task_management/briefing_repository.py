import os

from application.mobile_vault.interfaces import MobileVaultRepository
from domain.task_management.repository import BriefingRepository
from domain.task_management.task import DailyBriefing


class MobileVaultBriefingRepository(BriefingRepository):
    def __init__(self, mobile_vault_repo: MobileVaultRepository, inbox_dir: str):
        self.mobile_vault_repo = mobile_vault_repo
        self.inbox_dir = inbox_dir
        self.mobile_vault_repo.ensure_directory_exists(self.inbox_dir)

    def save(self, briefing: DailyBriefing) -> None:
        target_date = briefing.target_date
        filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"

        # Markdown文字列の生成
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

        content = "\n".join(lines) + "\n"

        try:
            self.mobile_vault_repo.save_file(content, self.inbox_dir, filename)
        except FileExistsError:
            from datetime import datetime
            now = datetime.now()
            backup_filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}_backup_{now.strftime('%H%M%S')}.md"
            old_path = os.path.join(self.inbox_dir, filename)
            new_path = os.path.join(self.inbox_dir, backup_filename)
            self.mobile_vault_repo.move_file(old_path, new_path)
            self.mobile_vault_repo.save_file(content, self.inbox_dir, filename)

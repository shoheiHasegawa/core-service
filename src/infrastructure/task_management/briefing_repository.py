import os
from datetime import date
from domain.task_management.repository import BriefingRepository
from domain.task_management.task import DailyBriefing
from application.mobile_vault.interfaces import MobileVaultRepository

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
        
        # 既存のファイルがあれば削除して上書き（冪等性）
        # MobileVaultRepositoryのsave_fileはFileExistsErrorを投げるため、事前に削除するかハンドリングする
        try:
            self.mobile_vault_repo.save_file(content, self.inbox_dir, filename)
        except FileExistsError:
            self.mobile_vault_repo.delete_file(os.path.join(self.inbox_dir, filename))
            self.mobile_vault_repo.save_file(content, self.inbox_dir, filename)

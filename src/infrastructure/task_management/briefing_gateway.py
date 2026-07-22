import os

from application.mobile_vault.interfaces import MobileVaultGateway
from domain.task_management.briefing_formatter import BriefingMarkdownFormatter
from domain.task_management.repository import BriefingGateway
from domain.task_management.task import DailyBriefing


class MobileVaultBriefingGateway(BriefingGateway):
    def __init__(self, mobile_vault_repo: MobileVaultGateway, inbox_dir: str):
        self.mobile_vault_repo = mobile_vault_repo
        self.inbox_dir = inbox_dir
        self.mobile_vault_repo.ensure_directory_exists(self.inbox_dir)

    def save(self, briefing: DailyBriefing) -> None:
        target_date = briefing.target_date
        filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"

        formatter = BriefingMarkdownFormatter()
        content = formatter.format(briefing)

        try:
            self.mobile_vault_repo.save_file(content, self.inbox_dir, filename)
        except FileExistsError:
            old_path = os.path.join(self.inbox_dir, filename)
            self.mobile_vault_repo.delete_file(old_path)
            self.mobile_vault_repo.save_file(content, self.inbox_dir, filename)

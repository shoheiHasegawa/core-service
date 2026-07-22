from application.mobile_vault.interfaces import MobileVaultGateway
from domain.task_management.briefing_formatter import BriefingMarkdownFormatter
from domain.task_management.repository import BriefingGateway
from domain.task_management.task import DailyBriefing


class MobileVaultBriefingGateway(BriefingGateway):
    def __init__(self, mobile_vault_repo: MobileVaultGateway):
        self.mobile_vault_repo = mobile_vault_repo

    def save(self, briefing: DailyBriefing) -> None:
        target_date = briefing.target_date
        filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"

        formatter = BriefingMarkdownFormatter()
        content = formatter.format(briefing)

        self.mobile_vault_repo.save_inbox_file(content, filename)

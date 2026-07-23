from typing import List

from domain.mobile_vault.dashboard_publisher import DashboardPublisher
from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.task_management.briefing_formatter import BriefingMarkdownFormatter
from domain.task_management.briefing_gateway import BriefingGateway
from domain.task_management.task import DailyBriefing


class MobileVaultBriefingGateway(BriefingGateway):
    def __init__(self, mobile_vault_publisher: DashboardPublisher, mobile_vault_reader: DashboardReader):
        self.mobile_vault_publisher = mobile_vault_publisher
        self.mobile_vault_reader = mobile_vault_reader

    def save(self, briefing: DailyBriefing) -> None:
        target_date = briefing.target_date
        filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"

        formatter = BriefingMarkdownFormatter()
        content = formatter.format(briefing)

        self.mobile_vault_publisher.publish(filename, content)

    def get_recent_briefing_contents(self) -> List[str]:
        return self.mobile_vault_reader.get_recent_dashboards()

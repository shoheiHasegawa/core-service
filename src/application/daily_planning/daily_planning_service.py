from domain.mobile_vault.dashboard_publisher import DashboardPublisher
from domain.task_management.briefing_formatter import BriefingMarkdownFormatter


class DailyPlanningService:
    """
    Facade for Daily Planning feature.
    Provides entry points for plan_day, record_worklogs, and sync_worklogs.
    Delegates actual logic to UseCases, and orchestrates cross-domain saving.
    """

    def __init__(
        self,
        plan_day_usecase,
        record_worklogs_usecase,
        sync_worklogs_usecase,
        mobile_vault_publisher: DashboardPublisher = None,
    ):
        self.plan_day_usecase = plan_day_usecase
        self.record_worklogs_usecase = record_worklogs_usecase
        self.sync_worklogs_usecase = sync_worklogs_usecase
        self.mobile_vault_publisher = mobile_vault_publisher

    def plan_day(self, target_date, sync_to_calendar: bool = False):
        # 1. 計画を作成
        briefing = self.plan_day_usecase.execute(target_date, sync_to_calendar=sync_to_calendar)

        # 2. フォーマットして Mobile Vault (他のService) に保存
        if self.mobile_vault_publisher:
            filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"
            formatter = BriefingMarkdownFormatter()
            content = formatter.format(briefing)
            self.mobile_vault_publisher.publish(filename, content)

        return briefing

    def record_worklogs(self, *args, **kwargs):
        return self.record_worklogs_usecase.execute(*args, **kwargs)

    def sync_worklogs(self, *args, **kwargs):
        return self.sync_worklogs_usecase.execute(*args, **kwargs)

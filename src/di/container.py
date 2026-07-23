from pathlib import Path

from sqlalchemy.orm import Session

from application.daily_planning.daily_planning_service import DailyPlanningService

# UseCases (Daily Planning)
from application.daily_planning.plan_day_usecase import PlanDayUseCase
from application.daily_planning.record_worklogs_usecase import RecordWorklogsUseCase
from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase
from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase

# UseCases (Mobile Vault)
from application.mobile_vault.retrieve_packets_usecase import RetrievePacketsUseCase
from application.second_brain.audit_zettelkasten_rules_usecase import AuditZettelkastenRulesUseCase

# UseCases (Second Brain)
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.register_permanent_note_usecase import RegisterPermanentNoteUseCase
from application.second_brain.search_notes_usecase import SearchNotesUseCase
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.refine_task_usecase import RefineTaskUseCase

# UseCases (Task Operations)
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from application.task_operations.task_operations_service import TaskOperationsService
from di.config import CoreServiceConfig

# Domain Interfaces
from domain.task_management.repository import ScheduleGateway
from infrastructure.calendar.config import CalendarConfig
from infrastructure.calendar.google_calendar_gateway import GoogleCalendarGateway
from infrastructure.mobile_vault.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from infrastructure.system_events.queue_system_event_gateway import QueueSystemEventGateway
from infrastructure.task_management.briefing_gateway import MobileVaultBriefingGateway

# Infrastructure & Adapters
from infrastructure.task_management.task_repository import SqlTaskRepository
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class DummyScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date, tasks):
        pass


class CoreServiceContainer:
    """
    Composition Root for core-service SDK.
    Assembles Infrastructure adapters and injects them into UseCases,
    then returns the Facade Services.
    """

    def __init__(self, config: CoreServiceConfig, session: Session):
        self.config = config
        self.session = session

        # --- 1. Instantiate Infrastructure Adapters ---
        self.task_repo = SqlTaskRepository(self.session)
        self.worklog_repo = SQLAlchemyWorklogRepository(self.session)

        self.mobile_vault_gateway = LocalFileMobileVaultGateway(
            self.config.mobile_inbox_dir, self.config.mobile_dashboard_dir
        )

        # Calendar
        cal_config = CalendarConfig(
            calendar_id=self.config.google_calendar_id, credentials_path=self.config.google_credentials_path
        )
        self.calendar_gateway = GoogleCalendarGateway(cal_config)
        self.schedule_gateway = DummyScheduleGateway()  # TODO: implement proper gateway

        # System Events
        self.system_event_gateway = QueueSystemEventGateway(queue_dir=Path(self.config.agent_queue_dir))

    def get_daily_planning_service(self) -> DailyPlanningService:
        # Assemble UseCases
        from infrastructure.task_management.recurring_task_repository import SqlRecurringTaskRepository

        plan_day_uc = PlanDayUseCase(
            task_repo=self.task_repo,
            schedule_gateway=self.schedule_gateway,
            briefing_repo=MobileVaultBriefingGateway(self.mobile_vault_gateway, self.mobile_vault_gateway),
            calendar_repo=self.calendar_gateway,
            recurring_task_repo=SqlRecurringTaskRepository(self.session),
        )
        record_worklogs_uc = RecordWorklogsUseCase(self.task_repo, self.worklog_repo)
        sync_worklogs_uc = SyncWorklogsUseCase(
            briefing_gateway=MobileVaultBriefingGateway(self.mobile_vault_gateway, self.mobile_vault_gateway),
            task_repository=self.task_repo,
            worklog_repository=self.worklog_repo,
        )
        # Return Facade
        return DailyPlanningService(plan_day_uc, record_worklogs_uc, sync_worklogs_uc)

    def get_task_operations_service(self) -> TaskOperationsService:
        register_task_uc = RegisterTaskUseCase(self.task_repo)
        refine_task_uc = RefineTaskUseCase(self.task_repo)
        return TaskOperationsService(register_task_uc, refine_task_uc)

    def get_second_brain_service(self) -> SecondBrainService:
        from application.second_brain.config import SecondBrainConfig
        from infrastructure.second_brain.local_file_second_brain_gateway import LocalFileSecondBrainGateway

        sb_config = SecondBrainConfig(
            inbox_dir=self.config.sb_inbox_dir,
            sense_making_dir=self.config.sb_sense_making_dir,
            permanent_notes_dir=self.config.sb_permanent_notes_dir,
            attachments_dir=self.config.sb_attachments_dir,
            inbox_template_path=self.config.sb_inbox_template_path,
            sense_making_template_path=self.config.sb_sense_making_template_path,
            permanent_note_template_path=self.config.sb_permanent_note_template_path,
            forbidden_patterns=self.config.sb_forbidden_patterns,
        )
        # 実際には、対象となる全ディレクトリをルートとしたGatewayを作成するか、個別に作成します
        # ひとまずinbox_dirをベースとする等の実装になりますが、今回は仮でinbox_dirを渡します
        sb_gateway = LocalFileSecondBrainGateway(base_path=self.config.sb_inbox_dir)

        return SecondBrainService(
            RegisterInboxNoteUseCase(sb_config, sb_gateway, self.task_repo),
            RegisterPermanentNoteUseCase(sb_config, sb_gateway),
            SearchNotesUseCase(sb_gateway),
            AuditZettelkastenRulesUseCase(sb_config, sb_gateway),
        )

    def get_mobile_vault_service(self) -> MobileVaultService:
        from domain.mobile_vault.parser import MarkdownImageParser

        return MobileVaultService(
            RetrievePacketsUseCase(
                receiver=self.mobile_vault_gateway, parser=MarkdownImageParser(), task_repository=self.task_repo
            ),
            PlaceDashboardUseCase(publisher=self.mobile_vault_gateway),
        )

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
from application.second_brain.audit_zettelkasten_rules_usecase import AuditZettelkastenRulesUseCase
from application.second_brain.config import SecondBrainConfig

# UseCases (Second Brain)
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.register_permanent_note_usecase import RegisterPermanentNoteUseCase
from application.second_brain.register_sense_making_note_usecase import RegisterSenseMakingNoteUseCase
from application.second_brain.search_notes_usecase import SearchNotesUseCase
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.refine_task_usecase import RefineTaskUseCase

# UseCases (Task Operations)
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from application.task_operations.task_operations_service import TaskOperationsService
from di.config import CoreServiceConfig
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser

# Domain Interfaces
from domain.task_management.schedule_gateway import ScheduleGateway
from infrastructure.google_api.google_calendar_gateway import CalendarConfig, GoogleCalendarGateway
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from infrastructure.local_file.local_file_second_brain_gateway import LocalFileSecondBrainGateway
from infrastructure.local_file.queue_system_event_gateway import QueueSystemEventGateway
from infrastructure.sqlalchemy.recurring_task_repository import SqlRecurringTaskRepository

# Infrastructure & Adapters
from infrastructure.sqlalchemy.task_repository import SqlTaskRepository
from infrastructure.sqlalchemy.worklog_repository import SQLAlchemyWorklogRepository


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
            self.config.mobile_inbox_dir, self.config.mobile_dashboard_dir, self.config.mobile_attachments_dir
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

        plan_day_uc = PlanDayUseCase(
            task_repo=self.task_repo,
            schedule_gateway=self.schedule_gateway,
            calendar_repo=self.calendar_gateway,
            recurring_task_repo=SqlRecurringTaskRepository(self.session),
        )
        record_worklogs_uc = RecordWorklogsUseCase(self.task_repo, self.worklog_repo)

        from domain.task_management.briefing_markdown_parser import BriefingMarkdownParser
        from infrastructure.system.system_clock import SystemClock
        from infrastructure.system.system_uuid_generator import SystemUUIDGenerator

        sync_worklogs_uc = SyncWorklogsUseCase(
            dashboard_reader=self.mobile_vault_gateway,
            task_repository=self.task_repo,
            worklog_repository=self.worklog_repo,
            parser=BriefingMarkdownParser(),
            clock=SystemClock(),
            uuid_generator=SystemUUIDGenerator(),
        )
        from application.daily_planning.auto_assign_tasks_usecase import AutoAssignTasksUseCase

        auto_assign_uc = AutoAssignTasksUseCase(self.task_repo)

        # Return Facade
        return DailyPlanningService(
            plan_day_uc,
            record_worklogs_uc,
            sync_worklogs_uc,
            auto_assign_tasks_usecase=auto_assign_uc,
            mobile_vault_publisher=self.mobile_vault_gateway,
        )

    def get_task_operations_service(self) -> TaskOperationsService:
        from infrastructure.system.system_uuid_generator import SystemUUIDGenerator

        register_task_uc = RegisterTaskUseCase(self.task_repo, SystemUUIDGenerator())
        refine_task_uc = RefineTaskUseCase(self.task_repo)
        return TaskOperationsService(register_task_uc, refine_task_uc)

    def get_second_brain_service(self) -> SecondBrainService:

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

        # SecondBrain全体をルートとする共有Gateway
        root_gateway = LocalFileSecondBrainGateway(base_path=str(Path(self.config.sb_inbox_dir).parent))

        return SecondBrainService(
            RegisterInboxNoteUseCase(
                save_dir=self.config.sb_inbox_dir,
                template_path=self.config.sb_inbox_template_path,
                repository=root_gateway,
                task_repository=self.task_repo,
            ),
            RegisterPermanentNoteUseCase(
                save_dir=self.config.sb_permanent_notes_dir,
                template_path=self.config.sb_permanent_note_template_path,
                repository=root_gateway,
            ),
            RegisterSenseMakingNoteUseCase(
                save_dir=self.config.sb_sense_making_dir,
                template_path=self.config.sb_sense_making_template_path,
                repository=root_gateway,
            ),
            SearchNotesUseCase(root_gateway),
            AuditZettelkastenRulesUseCase(sb_config, root_gateway),
        )

    def get_mobile_vault_service(self) -> MobileVaultService:
        from application.mobile_vault.peek_inbox_usecase import PeekInboxUseCase
        from application.mobile_vault.process_inbox_item_usecase import ProcessInboxItemUseCase

        parser = MarkdownImageParser()
        sb_gateway = LocalFileSecondBrainGateway(base_path=str(Path(self.config.sb_inbox_dir).parent))

        peek_inbox_uc = PeekInboxUseCase(self.mobile_vault_gateway, parser)
        process_inbox_item_uc = ProcessInboxItemUseCase(
            receiver=self.mobile_vault_gateway,
            second_brain_service=self.get_second_brain_service(),
            task_operations_service=self.get_task_operations_service(),
            sb_gateway=sb_gateway,
            sb_attachments_dir=self.config.sb_attachments_dir,
            parser=parser,
        )

        return MobileVaultService(
            peek_inbox_usecase=peek_inbox_uc,
            process_inbox_item_usecase=process_inbox_item_uc,
            place_dashboard_usecase=PlaceDashboardUseCase(publisher=self.mobile_vault_gateway),
        )

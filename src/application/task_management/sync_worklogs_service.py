import uuid
from datetime import datetime, timedelta

from application.mobile_vault.interfaces import MobileVaultGateway
from domain.mobile_vault.parser import BriefingMarkdownParser
from domain.task_management.repository import TaskRepository, WorklogRepository
from domain.task_management.task import Worklog


class SyncWorklogsService:
    def __init__(
        self,
        mobile_vault_gateway: MobileVaultGateway,
        task_repository: TaskRepository,
        worklog_repository: WorklogRepository,
    ):
        self.mobile_vault_gateway = mobile_vault_gateway
        self.task_repository = task_repository
        self.worklog_repository = worklog_repository
        self.parser = BriefingMarkdownParser()

    def sync(self) -> None:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        target_filenames = {
            f"Briefing_{yesterday.strftime('%Y-%m-%d')}.md",
            f"Briefing_{today.strftime('%Y-%m-%d')}.md",
        }

        files = self.mobile_vault_gateway.list_markdown_files()
        for filename in files:
            if filename not in target_filenames:
                continue

            content = self.mobile_vault_gateway.read_text(filename)
            completed_task_ids = self.parser.parse_completed_task_ids(content)

            for task_id in completed_task_ids:
                task = self.task_repository.find_by_id(task_id)
                if not task:
                    continue

                category = getattr(task.category, "value", task.category)
                task_type = getattr(task.task_type, "value", task.task_type)

                worklog = Worklog(
                    id=str(uuid.uuid4()),
                    task_id=task_id,
                    minutes=task.estimated_minutes,
                    is_completed=True,
                    target_date=today,
                    area_id=task.area_id,
                    category=category,
                    task_type=task_type,
                )
                self.worklog_repository.save(worklog)

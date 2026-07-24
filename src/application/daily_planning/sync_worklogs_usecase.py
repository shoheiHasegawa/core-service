import uuid
from datetime import datetime

from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.task_management.briefing_markdown_parser import BriefingMarkdownParser
from domain.task_management.task import Worklog
from domain.task_management.task_repository import TaskRepository
from domain.task_management.worklog_repository import WorklogRepository


class SyncWorklogsUseCase:
    """
    ダッシュボードファイルの内容から完了タスクをパースし、
    ワークログを生成・同期するユースケース。
    """

    def __init__(
        self,
        dashboard_reader: DashboardReader,
        task_repository: TaskRepository,
        worklog_repository: WorklogRepository,
    ):
        self.dashboard_reader = dashboard_reader
        self.task_repository = task_repository
        self.worklog_repository = worklog_repository
        self.parser = BriefingMarkdownParser()

    def execute(self) -> None:
        today = datetime.now().date()
        contents = self.dashboard_reader.get_recent_dashboards()

        for content in contents:
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

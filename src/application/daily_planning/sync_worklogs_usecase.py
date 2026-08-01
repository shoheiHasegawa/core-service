from datetime import timedelta

from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.system.clock import Clock
from domain.system.uuid_generator import UUIDGenerator
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
        parser: BriefingMarkdownParser,
        clock: Clock,
        uuid_generator: UUIDGenerator,
    ):
        self.dashboard_reader = dashboard_reader
        self.task_repository = task_repository
        self.worklog_repository = worklog_repository
        self.parser = parser
        self.clock = clock
        self.uuid_generator = uuid_generator

    def execute(self) -> None:
        today = self.clock.now().date()
        yesterday = today - timedelta(days=1)

        dates_to_check = [yesterday, today]

        for target_date in dates_to_check:
            filename = f"Briefing_{target_date.strftime('%Y-%m-%d')}.md"
            content = self.dashboard_reader.read_dashboard(filename)

            if not content:
                continue

            parsed_worklogs = self.parser.parse_worklogs(content, target_date)

            for pw in parsed_worklogs:
                # If neither completed, nor actual minutes provided, nor memo provided, it's untouched. Skip.
                if not pw.is_completed and pw.actual_minutes is None and pw.memo is None:
                    continue

                task = self.task_repository.find_by_id(pw.task_id)
                if not task:
                    continue

                # Fallback to estimated minutes if completed but no actual minutes provided
                actual_minutes = pw.actual_minutes if pw.actual_minutes is not None else task.estimated_minutes

                worklog = Worklog(
                    id=self.uuid_generator.generate(),
                    task_id=pw.task_id,
                    minutes=actual_minutes,
                    is_completed=pw.is_completed,
                    target_date=pw.target_date,
                    memo=pw.memo,
                    area_id=task.area_id,
                    category=task.category,
                    task_type=task.task_type,
                )
                self.worklog_repository.save(worklog)

                task.record_work(minutes=actual_minutes, is_completed=pw.is_completed, memo=pw.memo)
                self.task_repository.save(task)

            # パース・同期が成功裏に完了したら、元のBriefing.mdを削除（Leave No Trace）
            self.dashboard_reader.delete_dashboard(filename)

import os
import uuid

from application.mobile_vault.config import MobileVaultConfig
from application.mobile_vault.interfaces import IMobileVaultRepository
from domain.mobile_vault.parser import MarkdownImageParser
from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType


class MobileVaultService:
    def __init__(
        self,
        config: MobileVaultConfig,
        repository: IMobileVaultRepository,
        parser: MarkdownImageParser,
        task_repository: TaskRepository = None,
    ):
        self.config = config
        self.repository = repository
        self.parser = parser
        self.task_repository = task_repository

    def retrieve_packets(self) -> int:
        files = self.repository.list_markdown_files(str(self.config.inbox_dir))
        processed_count = 0
        for file_path in files:
            content = self.repository.read_text(file_path)
            self.parser.extract_images(content)

            if self.task_repository:
                filename = os.path.basename(file_path)
                task = Task(
                    id=str(uuid.uuid4()),
                    title=f"Process Packet: {filename}",
                    category=TaskCategory.MUST,
                    estimated_minutes=15,
                    task_type=TaskType.ONE_OFF,
                    status=TaskStatus.TODO,
                )
                self.task_repository.save(task)

            self.repository.delete_file(file_path)
            processed_count += 1
        return processed_count

    def place_dashboard(self, content: str, filename: str) -> str:
        self.repository.ensure_directory_exists(str(self.config.dashboard_dir))
        self.repository.save_file(content=content, directory=str(self.config.dashboard_dir), filename=filename)
        return str(self.config.dashboard_dir / filename)

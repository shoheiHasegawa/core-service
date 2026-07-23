import uuid
from typing import List

from application.second_brain.config import SecondBrainConfig
from domain.second_brain.repository import SecondBrainGateway
from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter
from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType


class RegisterInboxNoteUseCase:
    def __init__(
        self, config: SecondBrainConfig, repository: SecondBrainGateway, task_repository: TaskRepository = None
    ):
        self.config = config
        self.repository = repository
        self.task_repository = task_repository

    def _save_formatted_note(
        self, template_path: str, save_dir: str, title: str, content: str, tags: List[str], **kwargs
    ) -> bool:
        import datetime

        template_content = self.repository.read(template_path)
        formatter = ZettelkastenFormatter(template=template_content)
        formatted_content = formatter.format(
            title=title, body=content, current_time=datetime.datetime.now(), tags=tags, **kwargs
        )
        filename = self.repository.generate_safe_filename(title)
        save_path = f"{save_dir}/{filename}"
        self.repository.save(save_path, formatted_content)
        return True

    def execute(self, title: str, content: str, tags: List[str] = None) -> bool:
        success = self._save_formatted_note(
            template_path=self.config.inbox_template_path,
            save_dir=self.config.inbox_dir,
            title=title,
            content=content,
            tags=tags or [],
        )
        if success and self.task_repository:
            task = Task(
                id=str(uuid.uuid4()),
                title=f"Process idea: {title}",
                category=TaskCategory.MUST,
                estimated_minutes=15,
                task_type=TaskType.ONE_OFF,
                status=TaskStatus.TODO,
            )
            self.task_repository.save_tasks([task])
        return success

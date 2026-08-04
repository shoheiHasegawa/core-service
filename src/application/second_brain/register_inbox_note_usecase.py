import datetime
import os
import uuid

from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from domain.second_brain.repository import SecondBrainGateway
from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType
from domain.task_management.task_repository import TaskRepository


class RegisterInboxNoteUseCase:
    def __init__(
        self, save_dir: str, template_path: str, repository: SecondBrainGateway, task_repository: TaskRepository = None
    ):
        self.save_dir = save_dir
        self.template_path = template_path
        self.repository = repository
        self.task_repository = task_repository

    def _save_formatted_note(self, title: str, content: str, tags: list[str]) -> bool:

        template_content = self.repository.read(self.template_path)
        formatter = ZettelkastenFormatter(template=template_content)
        formatted_content = formatter.format(title=title, body=content, current_time=datetime.datetime.now(), tags=tags)
        filename = self.repository.generate_safe_filename(title)

        save_path = os.path.join(self.save_dir, filename)

        self.repository.save(save_path, formatted_content)
        return True

    def execute(self, dto: RegisterInboxNoteDto) -> bool:
        if not dto.title or not dto.title.strip():
            raise ValueError("Title cannot be empty")
        if not dto.content or not dto.content.strip():
            raise ValueError("Content cannot be empty")

        success = self._save_formatted_note(
            title=dto.title.strip(),
            content=dto.content,
            tags=dto.tags or [],
        )
        if success and self.task_repository:
            task = Task(
                id=str(uuid.uuid4()),
                title=f"Process idea: {dto.title}",
                category=TaskCategory.MUST,
                estimated_minutes=15,
                task_type=TaskType.ONE_OFF,
                status=TaskStatus.TODO,
            )
            self.task_repository.save_tasks([task])
        return success

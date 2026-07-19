import uuid
from typing import List

from application.second_brain.config import SecondBrainConfig
from domain.second_brain.repository import SecondBrainRepository
from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter
from domain.second_brain.zettelkasten_validator import ZettelkastenValidator
from domain.task_management.repository import TaskRepository
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType


class SecondBrainService:
    def __init__(
        self, config: SecondBrainConfig, repository: SecondBrainRepository, task_repository: TaskRepository = None
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

    def register_inbox_note(self, title: str, content: str, tags: List[str] = None) -> bool:
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
            self.task_repository.save(task)
        return success

    def register_sense_making_note(self, title: str, content: str, source: str = "", tags: List[str] = None) -> bool:
        return self._save_formatted_note(
            template_path=self.config.sense_making_template_path,
            save_dir=self.config.sense_making_dir,
            title=title,
            content=content,
            tags=tags or [],
            source=source,
        )

    def register_permanent_note(
        self,
        title: str,
        claim: str,
        context: str = "",
        connections: str = "",
        aliases: List[str] = None,
        tags: List[str] = None,
    ) -> bool:

        content = f"## 💡 Claim (核となる主張・知見)\n{claim}\n\n"
        content += f"## 🧭 Context (背景と深掘り)\n{context}\n\n"
        content += f"## 🔗 Connections (関連ノードと関係性)\n{connections}"

        return self._save_formatted_note(
            template_path=self.config.permanent_note_template_path,
            save_dir=self.config.permanent_notes_dir,
            title=title,
            content=content,
            tags=tags or [],
        )

    def search_notes(self, query: str) -> List[str]:
        return self.repository.search(query, extension=".md")

    def audit_zettelkasten_rules(self) -> List[str]:
        all_notes_content = self.repository.get_all_notes(extension=".md")
        validator = ZettelkastenValidator(forbidden_dirs=self.config.forbidden_patterns)

        all_errors = []
        for content in all_notes_content:
            is_valid, errors = validator.validate(content)
            if not is_valid:
                all_errors.extend(errors)

        return all_errors

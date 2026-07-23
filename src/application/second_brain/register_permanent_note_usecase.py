import datetime
import os

from application.second_brain.register_permanent_note_dto import RegisterPermanentNoteDto
from domain.second_brain.repository import SecondBrainGateway
from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter


class RegisterPermanentNoteUseCase:
    def __init__(self, save_dir: str, template_path: str, repository: SecondBrainGateway):
        self.save_dir = save_dir
        self.template_path = template_path
        self.repository = repository

    def _save_formatted_note(self, title: str, content: str, tags: list[str]) -> bool:

        template_content = self.repository.read(self.template_path)
        formatter = ZettelkastenFormatter(template=template_content)
        formatted_content = formatter.format(title=title, body=content, current_time=datetime.datetime.now(), tags=tags)
        filename = self.repository.generate_safe_filename(title)

        # Use simple os.path.join or f-string. Here, assuming save_dir does not have trailing slash.
        save_path = os.path.join(self.save_dir, filename)

        self.repository.save(save_path, formatted_content)
        return True

    def execute(self, dto: RegisterPermanentNoteDto) -> bool:
        content = f"## 💡 Claim (核となる主張・知見)\n{dto.claim}\n\n"
        content += f"## 🧭 Context (背景と深掘り)\n{dto.context}\n\n"
        content += f"## 🔗 Connections (関連ノードと関係性)\n{dto.connections}"

        return self._save_formatted_note(
            title=dto.title,
            content=content,
            tags=dto.tags or [],
        )

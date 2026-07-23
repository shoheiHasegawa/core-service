from typing import List

from application.second_brain.config import SecondBrainConfig
from domain.second_brain.repository import SecondBrainGateway
from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter


class RegisterPermanentNoteUseCase:
    def __init__(self, config: SecondBrainConfig, repository: SecondBrainGateway):
        self.config = config
        self.repository = repository

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

    def execute(
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

import datetime
import os

from application.second_brain.register_sense_making_note_dto import RegisterSenseMakingNoteDto
from domain.second_brain.repository import SecondBrainGateway
from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter


class RegisterSenseMakingNoteUseCase:
    def __init__(self, save_dir: str, template_path: str, repository: SecondBrainGateway):
        self.save_dir = save_dir
        self.template_path = template_path
        self.repository = repository

    def execute(self, dto: RegisterSenseMakingNoteDto) -> bool:

        template_content = self.repository.read(self.template_path)
        formatter = ZettelkastenFormatter(template=template_content)
        formatted_content = formatter.format(
            title=dto.title,
            body=dto.content,
            current_time=datetime.datetime.now(),
            tags=dto.tags,
            source=dto.source,
        )
        filename = self.repository.generate_safe_filename(dto.title)

        save_path = os.path.join(self.save_dir, filename)

        self.repository.save(save_path, formatted_content)
        return True

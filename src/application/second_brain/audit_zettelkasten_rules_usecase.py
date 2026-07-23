from typing import List

from application.second_brain.config import SecondBrainConfig
from domain.second_brain.repository import SecondBrainGateway
from domain.second_brain.zettelkasten_validator import ZettelkastenValidator


class AuditZettelkastenRulesUseCase:
    def __init__(self, config: SecondBrainConfig, repository: SecondBrainGateway):
        self.config = config
        self.repository = repository

    def execute(self) -> List[str]:
        all_notes_content = self.repository.get_all_notes(extension=".md")
        validator = ZettelkastenValidator(forbidden_dirs=self.config.forbidden_patterns)

        all_errors = []
        for content in all_notes_content:
            is_valid, errors = validator.validate(content)
            if not is_valid:
                all_errors.extend(errors)

        return all_errors

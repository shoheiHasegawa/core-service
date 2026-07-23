from unittest.mock import MagicMock

from application.second_brain.config import SecondBrainConfig
from application.second_brain.register_permanent_note_dto import RegisterPermanentNoteDto
from application.second_brain.register_permanent_note_usecase import RegisterPermanentNoteUseCase
from domain.second_brain.repository import SecondBrainGateway


def test_register_permanent_note():
    """[SB-PERM-01]"""
    repo = MagicMock(spec=SecondBrainGateway)
    config = SecondBrainConfig(
        inbox_dir="/inbox",
        sense_making_dir="/sense",
        permanent_notes_dir="/perm",
        attachments_dir="/att",
        inbox_template_path="/in",
        sense_making_template_path="/se",
        permanent_note_template_path="/pe",
        forbidden_patterns=[],
    )
    usecase = RegisterPermanentNoteUseCase(
        save_dir=config.permanent_notes_dir, template_path=config.permanent_note_template_path, repository=repo
    )

    dto = RegisterPermanentNoteDto(title="T", claim="C", context="", connections="", tags=[])
    result = usecase.execute(dto)

    assert result is True
    repo.save.assert_called_once()

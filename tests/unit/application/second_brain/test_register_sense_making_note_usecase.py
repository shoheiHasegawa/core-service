from unittest.mock import MagicMock

from application.second_brain.config import SecondBrainConfig
from application.second_brain.register_sense_making_note_dto import RegisterSenseMakingNoteDto
from application.second_brain.register_sense_making_note_usecase import RegisterSenseMakingNoteUseCase
from domain.second_brain.repository import SecondBrainGateway


def _create_mock_config():
    return SecondBrainConfig(
        inbox_dir="/inbox",
        sense_making_dir="/sense_making",
        permanent_notes_dir="/permanent",
        attachments_dir="/attachments",
        inbox_template_path="/inbox_template.md",
        sense_making_template_path="/sense_template.md",
        permanent_note_template_path="/permanent_template.md",
        forbidden_patterns=[],
    )


def test_register_sense_making_note():
    """[SB-SENSE-01]"""
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    usecase = RegisterSenseMakingNoteUseCase(
        save_dir=config.sense_making_dir, template_path=config.sense_making_template_path, repository=repo
    )

    dto = RegisterSenseMakingNoteDto(
        title="Sense Making", content="Incubation content", source="Source 123", tags=["test"]
    )
    result = usecase.execute(dto)

    assert result is True
    repo.save.assert_called_once()
    save_call_args = repo.save.call_args[0]
    assert save_call_args[0].startswith("/sense_making/")


def test_register_sense_making_note_empty_title():
    """[SB-BOUND-01]"""
    import pytest

    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    usecase = RegisterSenseMakingNoteUseCase(
        save_dir=config.sense_making_dir, template_path=config.sense_making_template_path, repository=repo
    )

    with pytest.raises(ValueError, match="Title cannot be empty") as exc_info:
        usecase.execute(RegisterSenseMakingNoteDto(title="", content="valid"))
    assert "Title cannot be empty" in str(exc_info.value)


def test_register_sense_making_note_empty_content():
    """[SB-BOUND-01]"""
    import pytest

    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    usecase = RegisterSenseMakingNoteUseCase(
        save_dir=config.sense_making_dir, template_path=config.sense_making_template_path, repository=repo
    )

    with pytest.raises(ValueError, match="Content cannot be empty") as exc_info:
        usecase.execute(RegisterSenseMakingNoteDto(title="valid", content="   "))
    assert "Content cannot be empty" in str(exc_info.value)

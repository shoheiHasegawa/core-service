from unittest.mock import MagicMock

from application.second_brain.config import SecondBrainConfig
from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from domain.second_brain.repository import SecondBrainGateway
from domain.task_management.task_repository import TaskRepository


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


def test_register_inbox_note():
    """[SB-INBOX-01]"""
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    task_repo = MagicMock(spec=TaskRepository)
    usecase = RegisterInboxNoteUseCase(
        save_dir=config.inbox_dir, template_path=config.inbox_template_path, repository=repo, task_repository=task_repo
    )

    dto = RegisterInboxNoteDto(title="Test Title", content="Test Content", tags=["test"])
    result = usecase.execute(dto)

    assert result is True
    repo.save.assert_called_once()
    save_call_args = repo.save.call_args[0]
    assert save_call_args[0].startswith("/inbox/")
    task_repo.save_tasks.assert_called_once()


def test_register_inbox_note_empty_title():
    """[SB-BOUND-01]"""
    import pytest

    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    usecase = RegisterInboxNoteUseCase(
        save_dir=config.inbox_dir, template_path=config.inbox_template_path, repository=repo
    )

    with pytest.raises(ValueError, match="Title cannot be empty") as exc_info:
        usecase.execute(RegisterInboxNoteDto(title="   ", content="Valid content"))
    assert "Title cannot be empty" in str(exc_info.value)


def test_register_inbox_note_empty_content():
    """[SB-BOUND-01]"""
    import pytest

    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    usecase = RegisterInboxNoteUseCase(
        save_dir=config.inbox_dir, template_path=config.inbox_template_path, repository=repo
    )

    with pytest.raises(ValueError, match="Content cannot be empty") as exc_info:
        usecase.execute(RegisterInboxNoteDto(title="Valid title", content="  "))
    assert "Content cannot be empty" in str(exc_info.value)

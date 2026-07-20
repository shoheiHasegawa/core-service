from unittest.mock import MagicMock

import pytest

from application.second_brain.config import SecondBrainConfig
from application.second_brain.service import SecondBrainService
from domain.second_brain.repository import SecondBrainRepository


@pytest.fixture
def mock_repo():
    return MagicMock(spec=SecondBrainRepository)


def test_second_brain_service_di():
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    config = SecondBrainConfig(
        inbox_dir="/path/to/inbox",
        sense_making_dir="/path/to/sense_making",
        permanent_notes_dir="/path/to/permanent",
        attachments_dir="/path/to/attachments",
        inbox_template_path="/path/to/inbox_template.md",
        sense_making_template_path="/path/to/sense_template.md",
        permanent_note_template_path="/path/to/permanent_template.md",
        forbidden_patterns=["draft", "temp"],
    )
    repo = MagicMock(spec=SecondBrainRepository)

    # Act
    service = SecondBrainService(config=config, repository=repo)

    # Assert
    assert service.config == config
    assert service.repository == repo


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
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainRepository)
    service = SecondBrainService(config=config, repository=repo)

    # Act
    result = service.register_inbox_note(title="Test Title", content="Test Content", tags=["test"])

    # Assert
    assert result is True
    repo.save.assert_called_once()
    # verify save path
    save_call_args = repo.save.call_args[0]
    assert save_call_args[0].startswith("/inbox/")


def test_register_sense_making_note():
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainRepository)
    service = SecondBrainService(config=config, repository=repo)

    # Act
    result = service.register_sense_making_note(
        title="Sense Making", content="Incubation content", source="Source 123", tags=["test"]
    )

    # Assert
    assert result is True
    repo.save.assert_called_once()
    # verify save path
    save_call_args = repo.save.call_args[0]
    assert save_call_args[0].startswith("/sense_making/")


def test_search_notes():
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainRepository)
    repo.search.return_value = ["note1.md", "note2.md"]
    service = SecondBrainService(config=config, repository=repo)

    # Act
    results = service.search_notes("query")

    # Assert
    assert results == ["note1.md", "note2.md"]
    repo.search.assert_called_once_with("query", extension=".md")


def test_audit_zettelkasten_rules():
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainRepository)
    repo.get_all_notes.return_value = ["note1.md", "note2.md"]
    service = SecondBrainService(config=config, repository=repo)

    # Act
    violations = service.audit_zettelkasten_rules()

    # Assert
    assert isinstance(violations, list)
    repo.get_all_notes.assert_called_once()

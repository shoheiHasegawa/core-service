from unittest.mock import MagicMock

from application.second_brain.audit_zettelkasten_rules_usecase import AuditZettelkastenRulesUseCase
from application.second_brain.config import SecondBrainConfig
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.register_sense_making_note_usecase import RegisterSenseMakingNoteUseCase
from application.second_brain.search_notes_usecase import SearchNotesUseCase
from domain.second_brain.repository import SecondBrainGateway
from domain.task_management.repository import TaskRepository


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
    usecase = RegisterInboxNoteUseCase(config=config, repository=repo, task_repository=task_repo)

    result = usecase.execute(title="Test Title", content="Test Content", tags=["test"])

    assert result is True
    repo.save.assert_called_once()
    save_call_args = repo.save.call_args[0]
    assert save_call_args[0].startswith("/inbox/")
    task_repo.save_tasks.assert_called_once()


def test_register_sense_making_note():
    """[SB-SENSE-01]"""
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    usecase = RegisterSenseMakingNoteUseCase(config=config, repository=repo)

    result = usecase.execute(title="Sense Making", content="Incubation content", source="Source 123", tags=["test"])

    assert result is True
    repo.save.assert_called_once()
    save_call_args = repo.save.call_args[0]
    assert save_call_args[0].startswith("/sense_making/")


def test_search_notes():
    """[SB-SEARCH-01]"""
    repo = MagicMock(spec=SecondBrainGateway)
    repo.search.return_value = ["note1.md", "note2.md"]
    usecase = SearchNotesUseCase(repository=repo)

    results = usecase.execute("query")

    assert results == ["note1.md", "note2.md"]
    repo.search.assert_called_once_with("query", extension=".md")


def test_audit_zettelkasten_rules():
    """[SB-AUDIT-01]"""
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    repo.get_all_notes.return_value = ["note1.md", "note2.md"]
    usecase = AuditZettelkastenRulesUseCase(config=config, repository=repo)

    violations = usecase.execute()

    assert isinstance(violations, list)
    repo.get_all_notes.assert_called_once()

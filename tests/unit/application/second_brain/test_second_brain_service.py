from unittest.mock import MagicMock

from application.second_brain.audit_zettelkasten_rules_usecase import AuditZettelkastenRulesUseCase
from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.register_permanent_note_usecase import RegisterPermanentNoteUseCase
from application.second_brain.register_sense_making_note_usecase import RegisterSenseMakingNoteUseCase
from application.second_brain.search_notes_usecase import SearchNotesUseCase
from application.second_brain.second_brain_service import SecondBrainService


def test_second_brain_service():
    """[SB-INBOX-01]"""
    inbox = MagicMock(spec=RegisterInboxNoteUseCase)
    sense = MagicMock(spec=RegisterSenseMakingNoteUseCase)
    perm = MagicMock(spec=RegisterPermanentNoteUseCase)
    search = MagicMock(spec=SearchNotesUseCase)
    audit = MagicMock(spec=AuditZettelkastenRulesUseCase)

    service = SecondBrainService(
        register_inbox_note_usecase=inbox,
        register_sense_making_note_usecase=sense,
        register_permanent_note_usecase=perm,
        search_notes_usecase=search,
        audit_zettelkasten_rules_usecase=audit,
    )

    dto = RegisterInboxNoteDto(title="T", content="C", tags=[])
    inbox.execute.return_value = True
    assert service.register_inbox_note(dto) is True
    inbox.execute.assert_called_once_with(dto)

    search.execute.return_value = []
    assert service.search_notes("query") == []
    search.execute.assert_called_once_with("query")

    audit.execute.return_value = []
    assert service.audit_zettelkasten_rules() == []
    audit.execute.assert_called_once()

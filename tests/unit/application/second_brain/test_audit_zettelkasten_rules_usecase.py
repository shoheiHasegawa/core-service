from unittest.mock import MagicMock

from application.second_brain.audit_zettelkasten_rules_usecase import AuditZettelkastenRulesUseCase
from application.second_brain.config import SecondBrainConfig
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


def test_audit_zettelkasten_rules():
    """[SB-AUDIT-01]"""
    config = _create_mock_config()
    repo = MagicMock(spec=SecondBrainGateway)
    repo.get_all_notes.return_value = ["note1.md", "note2.md"]
    usecase = AuditZettelkastenRulesUseCase(config=config, repository=repo)

    violations = usecase.execute()

    assert isinstance(violations, list)
    repo.get_all_notes.assert_called_once()

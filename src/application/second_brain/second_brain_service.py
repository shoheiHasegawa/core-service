from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.register_permanent_note_dto import RegisterPermanentNoteDto
from application.second_brain.register_sense_making_note_dto import RegisterSenseMakingNoteDto


class SecondBrainService:
    """
    Facade for Second Brain feature.
    Delegates actual logic to UseCases.
    """

    def __init__(
        self,
        register_inbox_note_usecase,
        register_permanent_note_usecase,
        register_sense_making_note_usecase,
        search_notes_usecase,
        audit_zettelkasten_rules_usecase,
    ):
        self.register_inbox_note_usecase = register_inbox_note_usecase
        self.register_permanent_note_usecase = register_permanent_note_usecase
        self.register_sense_making_note_usecase = register_sense_making_note_usecase
        self.search_notes_usecase = search_notes_usecase
        self.audit_zettelkasten_rules_usecase = audit_zettelkasten_rules_usecase

    def register_inbox_note(self, dto: RegisterInboxNoteDto):
        return self.register_inbox_note_usecase.execute(dto)

    def register_permanent_note(self, dto: RegisterPermanentNoteDto):
        return self.register_permanent_note_usecase.execute(dto)

    def register_sense_making_note(self, dto: RegisterSenseMakingNoteDto):
        return self.register_sense_making_note_usecase.execute(dto)

    def search_notes(self, query):
        return self.search_notes_usecase.execute(query)

    def audit_zettelkasten_rules(self):
        return self.audit_zettelkasten_rules_usecase.execute()

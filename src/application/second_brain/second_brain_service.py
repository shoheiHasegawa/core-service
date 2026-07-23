class SecondBrainService:
    """
    Facade for Second Brain feature.
    Delegates actual logic to UseCases.
    """

    def __init__(
        self,
        register_inbox_note_usecase,
        register_permanent_note_usecase,
        search_notes_usecase,
        audit_zettelkasten_rules_usecase,
    ):
        self.register_inbox_note_usecase = register_inbox_note_usecase
        self.register_permanent_note_usecase = register_permanent_note_usecase
        self.search_notes_usecase = search_notes_usecase
        self.audit_zettelkasten_rules_usecase = audit_zettelkasten_rules_usecase

    def register_inbox_note(self, content):
        return self.register_inbox_note_usecase.execute(content)

    def register_permanent_note(self, title, claim, context="", connections="", tags=None):
        return self.register_permanent_note_usecase.execute(
            title=title, claim=claim, context=context, connections=connections, tags=tags
        )

    def search_notes(self, query):
        return self.search_notes_usecase.execute(query)

    def audit_zettelkasten_rules(self):
        return self.audit_zettelkasten_rules_usecase.execute()

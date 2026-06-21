from typing import Dict, List

from domain.note_repository import IZettelkastenRepository
from domain.search_query import SearchQuery
from domain.zettelkasten_note import ValidationError, ZettelkastenNote


class ZettelkastenService:
    """Application Service for Zettelkasten"""

    def __init__(self, repository: IZettelkastenRepository):
        self.repository = repository

    def validate_all_notes(self) -> Dict[str, List[ValidationError]]:
        notes = self.repository.get_all()
        results = {}
        for note in notes:
            errors = note.validate()
            if errors:
                results[note.filename] = errors
        return results

    def search_notes(self, query: SearchQuery) -> List[ZettelkastenNote]:
        return self.repository.find_by_query(query)

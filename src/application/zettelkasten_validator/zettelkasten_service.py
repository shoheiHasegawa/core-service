from dataclasses import dataclass
from typing import Dict, List

from domain.note_repository import IZettelkastenRepository
from domain.search_query import SearchQuery
from domain.zettelkasten_note import ValidationError, ZettelkastenNote


@dataclass
class ZettelkastenConfig:
    """Configuration for Zettelkasten Service."""
    forbidden_patterns: List[str]
    # Future expansion: e.g., max_search_results: int = 100, exclude_tags: List[str] = field(default_factory=list)


class ZettelkastenService:
    """Application Service for Zettelkasten"""

    def __init__(self, config: ZettelkastenConfig, repository: IZettelkastenRepository):
        self.config = config
        self.repository = repository

    def validate_all_notes(self) -> Dict[str, List[ValidationError]]:
        notes = self.repository.get_all()
        results = {}
        for note in notes:
            errors = note.validate(self.config.forbidden_patterns)
            if errors:
                results[note.filename] = errors
        return results

    def search_notes(self, query: SearchQuery) -> List[ZettelkastenNote]:
        return self.repository.find_by_query(query)

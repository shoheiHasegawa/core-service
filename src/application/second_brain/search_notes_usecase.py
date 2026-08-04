from typing import List

from domain.second_brain.repository import SecondBrainGateway


class SearchNotesUseCase:
    def __init__(self, repository: SecondBrainGateway):
        self.repository = repository

    def execute(self, query: str) -> List[str]:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        return self.repository.search(query, extension=".md")

from typing import List

from domain.second_brain.repository import SecondBrainGateway


class SearchNotesUseCase:
    def __init__(self, repository: SecondBrainGateway):
        self.repository = repository

    def execute(self, query: str) -> List[str]:
        return self.repository.search(query, extension=".md")

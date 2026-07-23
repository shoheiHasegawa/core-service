from unittest.mock import MagicMock

from application.second_brain.search_notes_usecase import SearchNotesUseCase
from domain.second_brain.repository import SecondBrainGateway


def test_search_notes():
    """[SB-SEARCH-01]"""
    repo = MagicMock(spec=SecondBrainGateway)
    repo.search.return_value = ["note1.md", "note2.md"]
    usecase = SearchNotesUseCase(repository=repo)

    results = usecase.execute("query")

    assert results == ["note1.md", "note2.md"]
    repo.search.assert_called_once_with("query", extension=".md")

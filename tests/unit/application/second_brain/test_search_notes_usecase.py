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


def test_search_notes_empty_query():
    """[SB-BOUND-03]"""
    import pytest

    repo = MagicMock(spec=SecondBrainGateway)
    usecase = SearchNotesUseCase(repository=repo)

    with pytest.raises(ValueError, match="Query cannot be empty") as exc_info:
        usecase.execute("   ")
    assert "Query cannot be empty" in str(exc_info.value)

from typing import List

from domain.search_query import SearchQuery
from domain.zettelkasten_note import ZettelkastenNote


class IZettelkastenRepository:
    """Interface for Zettelkasten Note Repository"""

    def get_all(self) -> List[ZettelkastenNote]:
        raise NotImplementedError

    def find_by_query(self, query: SearchQuery) -> List[ZettelkastenNote]:
        raise NotImplementedError

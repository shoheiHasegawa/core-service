import os
import re
from typing import List, Dict
from core_service.domain.zettelkasten_note import ZettelkastenNote
from core_service.domain.search_query import SearchQuery

class IZettelkastenRepository:
    """Interface for Zettelkasten Note Repository"""
    def get_all(self) -> List[ZettelkastenNote]:
        raise NotImplementedError

    def find_by_query(self, query: SearchQuery) -> List[ZettelkastenNote]:
        raise NotImplementedError

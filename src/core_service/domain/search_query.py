from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchQuery:
    keyword: Optional[str] = None
    tag: Optional[str] = None
    alias: Optional[str] = None

    def is_empty(self) -> bool:
        return not self.keyword and not self.tag and not self.alias

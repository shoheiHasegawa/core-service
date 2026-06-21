import os
from typing import List

from domain.note_repository import IZettelkastenRepository
from domain.search_query import SearchQuery
from domain.zettelkasten_note import ZettelkastenNote
from infrastructure.markdown_parser import MarkdownParser


class LocalFileZettelkastenRepository(IZettelkastenRepository):
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def get_all(self) -> List[ZettelkastenNote]:
        notes = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if not file.endswith(".md"):
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse in infrastructure layer
                parser = MarkdownParser(content)
                keys = parser.parse_frontmatter_keys()
                lines = parser.parse_links_with_line_numbers()

                # Create Domain entity with parsed data
                notes.append(ZettelkastenNote(filename=filepath, frontmatter_keys=keys, lines_with_number=lines))
        return notes

    def find_by_query(self, query: SearchQuery) -> List[ZettelkastenNote]:
        # Implementation note: For a real system, we'd want a separate data model for search
        # or we'd store the raw content alongside the entity.
        # Since ZettelkastenNote no longer holds `content`, we must re-read or alter the design.
        # For this refactoring scope, we will re-read the file to perform the search in the infrastructure layer.

        if query.is_empty():
            return self.get_all()

        results = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if not file.endswith(".md"):
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                parser = MarkdownParser(content)
                tags, aliases = parser.extract_tags_and_aliases()

                match = False
                if query.tag and any(query.tag in t for t in tags):
                    match = True
                elif query.alias and any(query.alias in a for a in aliases):
                    match = True
                elif query.keyword and query.keyword.lower() in content.lower():
                    match = True

                if match:
                    keys = parser.parse_frontmatter_keys()
                    lines = parser.parse_links_with_line_numbers()
                    results.append(ZettelkastenNote(filename=filepath, frontmatter_keys=keys, lines_with_number=lines))

        return results

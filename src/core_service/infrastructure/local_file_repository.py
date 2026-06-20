import os
from typing import List
from core_service.domain.zettelkasten_note import ZettelkastenNote
from core_service.domain.search_query import SearchQuery
from core_service.domain.note_repository import IZettelkastenRepository

class LocalFileZettelkastenRepository(IZettelkastenRepository):
    def __init__(self, target_dir: str):
        self.target_dir = target_dir

    def get_all(self) -> List[ZettelkastenNote]:
        notes = []
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if not file.endswith('.md'):
                    continue
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                notes.append(ZettelkastenNote(filename=filepath, content=content))
        return notes

    def find_by_query(self, query: SearchQuery) -> List[ZettelkastenNote]:
        all_notes = self.get_all()
        if query.is_empty():
            return all_notes

        results = []
        for note in all_notes:
            match = False
            # Very simple tag/alias parsing (could be improved with a real YAML parser)
            frontmatter_lines = note.content.split('---')[1].split('\n') if '---' in note.content else []
            
            if query.tag:
                for line in frontmatter_lines:
                    if line.startswith('tags:') and query.tag in line:
                        match = True
                        break
            
            if not match and query.alias:
                for line in frontmatter_lines:
                    if line.startswith('aliases:') and query.alias in line:
                        match = True
                        break

            if not match and query.keyword:
                if query.keyword.lower() in note.content.lower():
                    match = True

            if match:
                results.append(note)

        return results

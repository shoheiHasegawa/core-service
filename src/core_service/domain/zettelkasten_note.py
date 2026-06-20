import re
from dataclasses import dataclass
from typing import List

@dataclass
class ValidationError:
    filename: str
    message: str

class ZettelkastenNote:
    REQUIRED_KEYS = {"id", "aliases", "tags", "created_at", "updated_at"}

    def __init__(self, filename: str, content: str):
        self.filename = filename
        self.content = content

    def validate(self) -> List[ValidationError]:
        errors = []
        errors.extend(self._validate_frontmatter())
        errors.extend(self._validate_links())
        return errors

    def _validate_frontmatter(self) -> List[ValidationError]:
        errors = []
        match = re.match(r'^---\s*\n(.*?)\n---\s*\n', self.content, re.DOTALL)
        if not match:
            return [ValidationError(self.filename, "Missing YAML frontmatter")]
        
        frontmatter = match.group(1)
        keys_found = set()
        for line in frontmatter.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if ':' in line:
                key = line.split(':', 1)[0].strip()
                keys_found.add(key)
        
        missing = self.REQUIRED_KEYS - keys_found
        if missing:
            errors.append(ValidationError(self.filename, f"Missing required YAML keys: {missing}"))
            
        return errors

    def _validate_links(self) -> List[ValidationError]:
        errors = []
        # Pattern to catch [text](path) or [[link]]
        # We want to forbid links containing /10_Areas/, /10_Projects/, /00_Inbox/
        forbidden_patterns = ['/10_Areas', '/10_Projects', '/00_Inbox', '/20_Sense_Making', '/30_Resources']
        
        lines = self.content.split('\n')
        for i, line in enumerate(lines):
            for fp in forbidden_patterns:
                if fp in line:
                    errors.append(ValidationError(self.filename, f"Forbidden outbound link to {fp} found on line {i+1}"))
        
        return errors

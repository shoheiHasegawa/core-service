from dataclasses import dataclass
from typing import List, Set, Tuple


@dataclass
class ValidationError:
    filename: str
    message: str


class ZettelkastenNote:
    REQUIRED_KEYS = {"id", "aliases", "tags", "created_at", "updated_at"}

    def __init__(self, filename: str, frontmatter_keys: Set[str], lines_with_number: List[Tuple[int, str]]):
        self.filename = filename
        self.frontmatter_keys = frontmatter_keys
        self.lines_with_number = lines_with_number

    def validate(self) -> List[ValidationError]:
        errors = []
        errors.extend(self._validate_frontmatter())
        errors.extend(self._validate_links())
        return errors

    def _validate_frontmatter(self) -> List[ValidationError]:
        errors = []
        if not self.frontmatter_keys:
            return [ValidationError(self.filename, "Missing YAML frontmatter")]

        missing = self.REQUIRED_KEYS - self.frontmatter_keys
        if missing:
            errors.append(ValidationError(self.filename, f"Missing required YAML keys: {missing}"))

        return errors

    def _validate_links(self) -> List[ValidationError]:
        errors = []
        forbidden_patterns = ["/10_Areas", "/10_Projects", "/00_Inbox", "/20_Sense_Making", "/30_Resources"]

        for line_num, line_text in self.lines_with_number:
            for fp in forbidden_patterns:
                if fp in line_text:
                    errors.append(
                        ValidationError(self.filename, f"Forbidden outbound link to {fp} found on line {line_num}")
                    )

        return errors

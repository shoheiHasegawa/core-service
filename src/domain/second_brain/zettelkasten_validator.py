import re
from typing import List, Tuple


class ZettelkastenValidator:
    def __init__(self, forbidden_dirs: List[str] = None):
        self.forbidden_dirs = forbidden_dirs or []

    def validate(self, content: str) -> Tuple[bool, List[str]]:
        errors = []
        if "id:" not in content:
            errors.append("Missing ID")
        if "tags:" not in content:
            errors.append("Missing tags")

        for fdir in self.forbidden_dirs:
            if fdir in content:
                errors.append(f"forbidden directory: {fdir}")

        # Tag format validation
        tags_match = re.search(r"^tags:\s*\[(.*?)\]", content, re.MULTILINE)
        if tags_match:
            tags_str = tags_match.group(1)
            if tags_str.strip():
                tags_list = [t.strip() for t in tags_str.split(",")]
                for tag in tags_list:
                    # Allow nested hierarchies by accepting multiple slashes,
                    # e.g., Knowledge/Productivity (but rule is snake_case english)
                    # The rule is: english snake_case and hierarchical.
                    # ^[a-z0-9_]+(/[a-z0-9_]+)+$
                    if not re.match(r"^[a-z0-9_]+(/[a-z0-9_]+)+$", tag):
                        msg = (
                            f"Tag '{tag}' violates formatting rule "
                            "(must be english, snake_case and hierarchical like 'domain/concept')"
                        )
                        errors.append(msg)

        return len(errors) == 0, errors

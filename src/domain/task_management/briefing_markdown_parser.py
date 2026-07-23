import re


class BriefingMarkdownParser:
    def parse_completed_task_ids(self, content: str) -> list[str]:
        ids = []
        for line in content.splitlines():
            if line.strip().startswith("- [x]"):
                match = re.search(r"<!--\s*id:\s*(.+?)\s*-->", line)
                if match:
                    ids.append(match.group(1).strip())
        return ids

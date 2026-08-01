import re
from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class ParsedWorklog:
    task_id: str
    is_completed: bool
    actual_minutes: Optional[int]
    memo: Optional[str]
    target_date: Optional[date]


class BriefingMarkdownParser:
    def parse_worklogs(self, content: str, target_date: date) -> List[ParsedWorklog]:

        worklogs = []
        current_worklog = None

        for line in content.splitlines():
            stripped = line.strip()

            if stripped.startswith("- [ ]") or stripped.startswith("- [x]") or stripped.startswith("- [X]"):
                is_completed = stripped.lower().startswith("- [x]")

                id_match = re.search(r"<!--\s*id:\s*(.+?)\s*-->", line)
                if id_match:
                    task_id = id_match.group(1).strip()

                    line_without_id = re.sub(r"<!--.*?-->", "", stripped).strip()
                    min_match = re.search(r"\s+(\d+)$", line_without_id)
                    actual_minutes = int(min_match.group(1)) if min_match else None

                    current_worklog = ParsedWorklog(
                        task_id=task_id,
                        is_completed=is_completed,
                        actual_minutes=actual_minutes,
                        memo=None,
                        target_date=target_date,
                    )
                    worklogs.append(current_worklog)
                continue

            if current_worklog and stripped.startswith("メモ:"):
                memo_text = stripped[len("メモ:") :].strip()
                current_worklog.memo = memo_text

        return worklogs

    def parse_completed_task_ids(self, content: str) -> list[str]:
        ids = []
        for line in content.splitlines():
            if line.strip().startswith("- [x]"):
                match = re.search(r"<!--\s*id:\s*(.+?)\s*-->", line)
                if match:
                    ids.append(match.group(1).strip())
        return ids

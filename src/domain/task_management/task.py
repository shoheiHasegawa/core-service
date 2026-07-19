from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class TaskCategory(Enum):
    MUST = "M"
    SHOULD = "S"
    WANT = "W"


class TaskType(Enum):
    ONE_OFF = "ONE_OFF"
    ROUTINE = "ROUTINE"
    RECURRING = "RECURRING"


class TaskStatus(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    INCOMPLETE = "INCOMPLETE"


class WarningFlag(Enum):
    W_RATIO_LOW = "W_RATIO_LOW"
    DEADLINE_EXCEEDED = "DEADLINE_EXCEEDED"


@dataclass
class Task:
    id: str
    title: str
    category: TaskCategory
    estimated_minutes: int
    task_type: TaskType = TaskType.ONE_OFF
    area_id: str = "00_Unknown"
    cumulative_minutes: int = 0
    status: TaskStatus = TaskStatus.TODO
    actual_minutes: int = 0
    deadline: Optional[date] = None
    target_date: Optional[date] = None
    dependencies: List[str] = field(default_factory=list)
    reference_id: Optional[str] = None
    last_memo: Optional[str] = None
    is_deep_work: bool = False

    def calculate_lfd(self) -> Optional[date]:
        """依存関係と期限から Latest Finish Date (LFD) を計算する"""
        return self.deadline  # TODO: 依存グラフを遡って真のLFDを計算するロジックを実装

    def record_work(self, minutes: int, is_completed: bool, memo: Optional[str] = None) -> None:
        self.actual_minutes += minutes
        if memo is not None:
            self.last_memo = memo
        if is_completed:
            self.status = TaskStatus.COMPLETED
        elif self.status == TaskStatus.TODO:
            self.status = TaskStatus.IN_PROGRESS


@dataclass
class DailyBriefing:
    target_date: date
    scheduled_tasks: List[Task]
    warning_flags: List[WarningFlag] = field(default_factory=list)
    motivation_message: str = ""


@dataclass
class Worklog:
    id: str
    task_id: str
    minutes: int
    is_completed: bool = False
    target_date: Optional[date] = None
    memo: Optional[str] = None

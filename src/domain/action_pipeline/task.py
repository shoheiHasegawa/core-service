from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class TaskCategory(Enum):
    MUST = "M"
    SHOULD = "S"
    WANT = "W"


class EnergyLevel(Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


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
    energy_level: EnergyLevel
    estimated_minutes: int
    status: TaskStatus = TaskStatus.TODO
    actual_minutes: int = 0
    deadline: Optional[date] = None
    target_date: Optional[date] = None
    dependencies: List[str] = field(default_factory=list)

    def calculate_lfd(self) -> Optional[date]:
        """依存関係と期限から Latest Finish Date (LFD) を計算する"""
        return self.deadline  # TODO: 依存グラフを遡って真のLFDを計算するロジックを実装


@dataclass
class DailyBriefing:
    target_date: date
    scheduled_tasks: List[Task]
    warning_flags: List[WarningFlag] = field(default_factory=list)
    motivation_message: str = ""

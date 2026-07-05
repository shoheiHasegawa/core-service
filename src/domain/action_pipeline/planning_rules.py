from typing import List

from .task import EnergyLevel, Task, TaskCategory, WarningFlag


class WIPAllocationPolicy:
    MAX_MUST_WIP = 3

    @staticmethod
    def apply(ready_tasks: List[Task]) -> List[Task]:
        """[SCENARIO-02] WIP制限: 1日のMUSTタスクは最大3つまで"""
        must_tasks = [t for t in ready_tasks if t.category == TaskCategory.MUST][: WIPAllocationPolicy.MAX_MUST_WIP]
        other_tasks = [t for t in ready_tasks if t.category != TaskCategory.MUST]
        return must_tasks + other_tasks


class ContextBatchingPolicy:
    @staticmethod
    def apply(tasks: List[Task]) -> List[Task]:
        """[SCENARIO-05] コンテキストバッチング: 深い⇔浅い作業の往復を最小化するためにソート"""
        high = [t for t in tasks if t.energy_level == EnergyLevel.HIGH]
        med = [t for t in tasks if t.energy_level == EnergyLevel.MEDIUM]
        low = [t for t in tasks if t.energy_level == EnergyLevel.LOW]
        return high + med + low


class SchedulingValidator:
    @staticmethod
    def validate(tasks: List[Task]) -> List[WarningFlag]:
        """[SCENARIO-03] Wタスク不足警告などの検証"""
        flags = []
        w_tasks = [t for t in tasks if t.category == TaskCategory.WANT]
        if tasks and len(w_tasks) / len(tasks) < 0.2:
            flags.append(WarningFlag.W_RATIO_LOW)
        return flags

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Protocol

from .task import Task, TaskCategory, WarningFlag


class WIPAllocationPolicy:
    MAX_MUST_WIP = 3

    @staticmethod
    def apply(ready_tasks: List[Task]) -> List[Task]:
        """[TASK-02] WIP制限: 1日のMUSTタスクは最大3つまで"""
        must_tasks = [t for t in ready_tasks if t.category == TaskCategory.MUST][: WIPAllocationPolicy.MAX_MUST_WIP]
        other_tasks = [t for t in ready_tasks if t.category != TaskCategory.MUST]
        return must_tasks + other_tasks


class ContextBatchingPolicy:
    @staticmethod
    def apply(tasks: List[Task]) -> List[Task]:
        """[TASK-05] コンテキストバッチング: 深い⇔浅い作業の往復を最小化するためにソート"""
        # 深い作業と浅い作業を分けることで往復を1回に抑える
        return sorted(tasks, key=lambda t: not getattr(t, "is_deep_work", False))


class TaskCollectionValidator(Protocol):
    def validate(self, tasks: List[Task]) -> List[WarningFlag]: ...


class WRatioValidator:
    MIN_W_RATIO = 0.2

    def validate(self, tasks: List[Task]) -> List[WarningFlag]:
        w_tasks = [t for t in tasks if t.category == TaskCategory.WANT]
        if tasks and len(w_tasks) / len(tasks) < self.MIN_W_RATIO:
            return [WarningFlag.W_RATIO_LOW]
        return []


class DeadlineValidator:
    def validate(self, tasks: List[Task]) -> List[WarningFlag]:
        today = date.today()
        for t in tasks:
            if t.deadline and t.deadline < today:
                return [WarningFlag.DEADLINE_EXCEEDED]
        return []


class SchedulingValidator:
    @staticmethod
    def validate(tasks: List[Task]) -> List[WarningFlag]:
        """[TASK-03] Wタスク不足警告などの検証 [TASK-04] LFD超過警告"""
        validators: List[TaskCollectionValidator] = [WRatioValidator(), DeadlineValidator()]
        flags = []
        for validator in validators:
            flags.extend(validator.validate(tasks))
        return flags


class DependencyPolicy:
    @staticmethod
    def filter_ready(tasks: List[Task], completed_task_ids: List[str]) -> List[Task]:
        """[TASK-06] 未Readyタスクの自動不可視化"""
        ready_tasks = []
        completed_set = set(completed_task_ids)
        for t in tasks:
            if all(dep in completed_set for dep in t.dependencies):
                ready_tasks.append(t)
        return ready_tasks


class StrategicInvestmentPolicy:
    STRATEGIC_INVESTMENT_RATIO = 0.20

    @staticmethod
    def allocate(available_minutes: int, s_tasks: List[Task]) -> List[Task]:
        """[TASK-07] 戦略的投資枠の強制ブロック"""
        target_minutes = available_minutes * StrategicInvestmentPolicy.STRATEGIC_INVESTMENT_RATIO
        allocated = []
        allocated_minutes = 0
        for t in s_tasks:
            if allocated_minutes >= target_minutes:
                break
            allocated.append(t)
            allocated_minutes += t.estimated_minutes
        return allocated


class OrphanTaskPolicy:
    UNKNOWN_AREA_ID = "00_Unknown"

    @staticmethod
    def filter(tasks: List[Task]) -> List[Task]:
        """[TASK-08] 孤立タスクの排除"""
        return [t for t in tasks if t.area_id is not None and t.area_id != OrphanTaskPolicy.UNKNOWN_AREA_ID]


class ScheduleBuilder:
    DEEP_WORK_MAX_CONTINUOUS_MINUTES = 90
    BREAK_MINUTES = 15
    SHUTDOWN_RITUAL_MINUTES = 30

    @staticmethod
    def build(start_time: datetime, tasks: List[Task]) -> List[Dict[str, Any]]:
        """[TASK-09] ディープワーク連続稼働リミット到達"""
        schedule = []
        current_time = start_time

        for t in tasks:
            remaining_minutes = t.estimated_minutes
            while remaining_minutes > 0:
                is_deep_work = getattr(t, "is_deep_work", False)
                if is_deep_work and remaining_minutes > ScheduleBuilder.DEEP_WORK_MAX_CONTINUOUS_MINUTES:
                    # 分割
                    chunk_minutes = ScheduleBuilder.DEEP_WORK_MAX_CONTINUOUS_MINUTES
                    end_time = current_time + timedelta(minutes=chunk_minutes)
                    schedule.append({"task": t, "start": current_time, "end": end_time})
                    current_time = end_time
                    remaining_minutes -= chunk_minutes

                    # 休憩
                    break_end = current_time + timedelta(minutes=ScheduleBuilder.BREAK_MINUTES)
                    break_task = Task(
                        id="break",
                        title="Break",
                        category=TaskCategory.WANT,
                        estimated_minutes=ScheduleBuilder.BREAK_MINUTES,
                    )
                    schedule.append({"task": break_task, "start": current_time, "end": break_end})
                    current_time = break_end
                else:
                    end_time = current_time + timedelta(minutes=remaining_minutes)
                    schedule.append({"task": t, "start": current_time, "end": end_time})
                    current_time = end_time
                    remaining_minutes = 0

        return schedule

    @staticmethod
    def build_with_end(start_time: datetime, end_time: datetime, tasks: List[Task]) -> List[Dict[str, Any]]:
        """[TASK-11] シャットダウン・リチュアルの固定配置"""
        schedule = ScheduleBuilder.build(start_time, tasks)

        shutdown_start = end_time - timedelta(minutes=ScheduleBuilder.SHUTDOWN_RITUAL_MINUTES)
        shutdown_task = Task(
            id="shutdown",
            title="Shutdown Ritual",
            category=TaskCategory.MUST,
            estimated_minutes=ScheduleBuilder.SHUTDOWN_RITUAL_MINUTES,
        )

        schedule.append({"task": shutdown_task, "start": shutdown_start, "end": end_time})
        return schedule


class CircadianRhythmPolicy:
    DIP_START_HOUR = 13
    DIP_END_HOUR = 15

    @staticmethod
    def validate(schedule: List[Dict[str, Any]]) -> bool:
        """[TASK-10] サーカディアン・ディップの自動処理"""
        for item in schedule:
            start_time = item["start"]
            end_time = item["end"]
            task = item["task"]

            dip_start = start_time.replace(hour=CircadianRhythmPolicy.DIP_START_HOUR, minute=0, second=0, microsecond=0)
            dip_end = start_time.replace(hour=CircadianRhythmPolicy.DIP_END_HOUR, minute=0, second=0, microsecond=0)

            if max(start_time, dip_start) < min(end_time, dip_end):
                if getattr(task, "is_deep_work", False) and task.category != TaskCategory.WANT:
                    return False
        return True


class MorningDeepWorkPolicy:
    MORNING_END_HOUR = 12

    @staticmethod
    def validate(schedule: List[Dict[str, Any]]) -> bool:
        """[TASK-12] 午前中の浅い作業ブロックエラー"""
        for item in schedule:
            start_time = item["start"]
            task = item["task"]

            if start_time.hour < MorningDeepWorkPolicy.MORNING_END_HOUR:
                if not getattr(task, "is_deep_work", False):
                    return False
        return True

from datetime import date, datetime, timedelta
from typing import Optional

import holidays

from domain.task_management.calendar_gateway import CalendarGateway
from domain.task_management.planning_rules import (
    ContextBatchingPolicy,
    DependencyPolicy,
    MorningDeepWorkPolicy,
    OrphanTaskPolicy,
    RecoveryFirstPolicy,
    ScheduleBuilder,
    SchedulingValidator,
    WIPAllocationPolicy,
)
from domain.task_management.schedule_gateway import ScheduleGateway
from domain.task_management.task import DailyBriefing
from domain.task_management.task_repository import TaskRepository


class PlanDayUseCase:
    """
    1日の計画（Daily Briefing）を生成し、カレンダーへ出力するユースケース。
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        schedule_gateway: ScheduleGateway,
        calendar_repo: Optional[CalendarGateway] = None,
        recurring_task_repo=None,
    ) -> None:
        self.task_repo = task_repo
        self.schedule_gateway = schedule_gateway
        self.calendar_repo = calendar_repo
        self.recurring_task_repo = recurring_task_repo

    def _is_holiday(self, target_date: date) -> bool:
        if target_date in holidays.JP():
            return True
        if self.calendar_repo:
            all_day_events = self.calendar_repo.fetch_all_day_events(target_date)
            return any(keyword in event for event in all_day_events for keyword in ["有休", "有給", "休暇"])
        return False

    def execute(self, target_date: date, sync_to_calendar: bool = False) -> DailyBriefing:
        is_holiday = self._is_holiday(target_date)

        ready_tasks = self.task_repo.get_ready_tasks_for_date(target_date)

        # 未Readyタスク・孤立タスクの除外
        tasks = OrphanTaskPolicy.filter(ready_tasks)
        tasks = DependencyPolicy.filter_ready(tasks, [])

        # WIP制限
        tasks = WIPAllocationPolicy.apply(tasks)

        # コンテキストバッチング
        tasks = ContextBatchingPolicy.apply(tasks)

        # Morning Deep Work 優先
        tasks = MorningDeepWorkPolicy.prioritize(tasks)

        # リカバリーファースト (睡眠とWANTを最優先に)
        tasks = RecoveryFirstPolicy.apply(tasks, target_date)

        # タイムスケジュール構築
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = start_time + timedelta(hours=23)

        # 定期タスクの抽出と固定ブロック化
        fixed_tasks = []
        if self.recurring_task_repo:
            active_recurring = self.recurring_task_repo.find_active_by_date(target_date)
            for rt in active_recurring:
                if rt.is_scheduled_on(target_date, is_holiday):
                    fixed_tasks.append(rt.to_task(target_date))

        scheduled_tasks, deferred_tasks = ScheduleBuilder.assign_times(start_time, tasks, end_time, fixed_tasks)

        # 警告フラグ
        warning_flags = SchedulingValidator.validate(scheduled_tasks)

        briefing = DailyBriefing(
            target_date=target_date,
            scheduled_tasks=scheduled_tasks,
            deferred_tasks=deferred_tasks,
            warning_flags=warning_flags,
        )

        # カレンダー同期と出力
        self.schedule_gateway.sync_schedule(target_date, scheduled_tasks)

        if sync_to_calendar and self.calendar_repo:
            self.calendar_repo.sync_daily_briefing(target_date, scheduled_tasks)

        return briefing

from datetime import date

from domain.action_pipeline.planning_rules import ContextBatchingPolicy, SchedulingValidator, WIPAllocationPolicy
from domain.action_pipeline.repository import IBriefingRepository, IScheduleGateway, ITaskRepository
from domain.action_pipeline.task import DailyBriefing


class DailyPlanningService:
    def __init__(
        self, task_repo: ITaskRepository, schedule_gateway: IScheduleGateway, briefing_repo: IBriefingRepository
    ) -> None:
        self.task_repo = task_repo
        self.schedule_gateway = schedule_gateway
        self.briefing_repo = briefing_repo

    def generate_today_plan(self, target_date: date) -> DailyBriefing:
        # [SCENARIO-06, 08] 未Ready・孤立タスクはRepository層のクエリ時点で除外されている前提
        ready_tasks = self.task_repo.get_ready_tasks_for_date(target_date)

        # [SCENARIO-02] WIP制限の適用 (Domain Rule)
        allocated_tasks = WIPAllocationPolicy.apply(ready_tasks)

        # [SCENARIO-05] コンテキストバッチングの適用 (Domain Rule)
        batched_tasks = ContextBatchingPolicy.apply(allocated_tasks)

        # [SCENARIO-03] 異常系検証と警告フラグの生成 (Domain Rule)
        warning_flags = SchedulingValidator.validate(batched_tasks)

        briefing = DailyBriefing(target_date=target_date, scheduled_tasks=batched_tasks, warning_flags=warning_flags)

        # カレンダー同期と出力
        self.schedule_gateway.sync_schedule(target_date, batched_tasks)
        self.briefing_repo.save(briefing)

        return briefing

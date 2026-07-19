from datetime import date
from typing import List

from domain.task_management.planning_rules import ContextBatchingPolicy, SchedulingValidator, WIPAllocationPolicy
from domain.task_management.repository import BriefingRepository, ScheduleGateway, TaskRepository, WorklogRepository
from domain.task_management.task import DailyBriefing, Worklog


class DailyActionService:
    def __init__(
        self,
        task_repo: TaskRepository,
        schedule_gateway: ScheduleGateway,
        briefing_repo: BriefingRepository,
        worklog_repo: WorklogRepository,
    ) -> None:
        self.task_repo = task_repo
        self.schedule_gateway = schedule_gateway
        self.briefing_repo = briefing_repo
        self.worklog_repo = worklog_repo

    def plan_day(self, target_date: date) -> DailyBriefing:
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

    def record_worklogs(self, target_date: date, worklogs: List[Worklog]) -> None:
        if not worklogs:
            return

        task_ids = [w.task_id for w in worklogs]
        tasks = self.task_repo.get_tasks_by_ids(task_ids)
        task_map = {t.id: t for t in tasks}

        updated_tasks = []
        for w in worklogs:
            if w.task_id in task_map:
                task = task_map[w.task_id]

                # 指定日付の既存 Worklog を取得
                existing_worklogs = self.worklog_repo.find_by_task_and_date(w.task_id, target_date)
                existing_minutes = sum([ew.minutes for ew in existing_worklogs])

                # 差分（Delta）だけを加算
                delta = w.minutes - existing_minutes
                task.record_work(delta, w.is_completed, w.memo)

                w.target_date = target_date
                self.worklog_repo.save(w)
                updated_tasks.append(task)

        if updated_tasks:
            self.task_repo.save_tasks(updated_tasks)

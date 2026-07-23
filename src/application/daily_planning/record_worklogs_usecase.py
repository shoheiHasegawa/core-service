from datetime import date
from typing import List

from domain.task_management.task import Worklog
from domain.task_management.task_repository import TaskRepository
from domain.task_management.worklog_repository import WorklogRepository


class RecordWorklogsUseCase:
    """
    指定された日の作業ログ（Worklog）をタスクに記録・更新するユースケース。
    """

    def __init__(self, task_repo: TaskRepository, worklog_repo: WorklogRepository) -> None:
        self.task_repo = task_repo
        self.worklog_repo = worklog_repo

    def execute(self, target_date: date, worklogs: List[Worklog]) -> None:
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

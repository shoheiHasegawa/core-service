from datetime import date

from domain.task_management.planning_rules import WIPAllocationPolicy
from domain.task_management.task import TaskCategory, TaskType
from domain.task_management.task_repository import TaskRepository


class AutoAssignTasksUseCase:
    """
    未完了タスクの持ち越しと、バックログからの優先度ベースの自動アサインを行うユースケース。
    """

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    def execute(self, target_date: date) -> None:
        # 1. Roll-over uncompleted past tasks
        past_tasks = self.task_repository.get_uncompleted_past_tasks(target_date)
        rollover_tasks = [t for t in past_tasks if t.task_type == TaskType.ONE_OFF]
        for t in rollover_tasks:
            t.target_date = target_date

        if rollover_tasks:
            self.task_repository.save_tasks(rollover_tasks)

        # 2. Check current MUST WIP limit for the target date
        # (This includes the rolled-over tasks)
        ready_tasks = self.task_repository.get_ready_tasks_for_date(target_date)
        current_must_tasks = [t for t in ready_tasks if t.category == TaskCategory.MUST]

        remaining_must_wip = max(0, WIPAllocationPolicy.MAX_MUST_WIP - len(current_must_tasks))

        # 3. Assign new tasks from backlog if there is remaining WIP
        if remaining_must_wip > 0:
            backlog = self.task_repository.get_backlog_tasks()

            energy_score = {"High": 3, "Medium": 2, "Low": 1, None: 0}

            backlog.sort(
                key=lambda t: (
                    t.category.value,  # MUST=1, SHOULD=2, WANT=3 (昇順で優先)
                    -energy_score.get(t.energy_level, 0),  # energy_levelが高いほど優先
                )
            )

            assigned_tasks = []
            must_assigned_count = 0

            for t in backlog:
                if t.category == TaskCategory.MUST:
                    if must_assigned_count < remaining_must_wip:
                        t.target_date = target_date
                        assigned_tasks.append(t)
                        must_assigned_count += 1
                else:
                    break  # Since it's sorted by category, once we hit non-MUST we can break the MUST assignment

            # Add up to 2 SHOULD/WANT tasks to ensure progress
            should_wants = [t for t in backlog if t.category != TaskCategory.MUST][:2]
            for t in should_wants:
                t.target_date = target_date
                assigned_tasks.append(t)

            if assigned_tasks:
                self.task_repository.save_tasks(assigned_tasks)

from datetime import date

from application.daily_planning.auto_assign_tasks_usecase import AutoAssignTasksUseCase
from domain.task_management.task import Task, TaskCategory, TaskType


class MockTaskRepositoryForAutoAssign:
    def __init__(self):
        self.saved_tasks = []
        self.past_tasks = []
        self.ready_tasks = []
        self.backlog_tasks = []

    def get_uncompleted_past_tasks(self, target_date):
        return self.past_tasks

    def get_ready_tasks_for_date(self, target_date):
        return self.ready_tasks

    def get_backlog_tasks(self):
        return self.backlog_tasks

    def save_tasks(self, tasks):
        self.saved_tasks.extend(tasks)


def test_auto_assign_tasks_rollover_and_backlog():
    """
    [TM-PLAN-01] 未完了の過去タスクが引き継がれ、残りのWIP枠に応じてMUST/SHOULDタスクがアサインされることを検証する。
    """
    repo = MockTaskRepositoryForAutoAssign()

    # 1. Setup past uncompleted tasks
    past_task = Task(id="past1", title="Past", category=TaskCategory.MUST, estimated_minutes=30)
    repo.past_tasks = [past_task]

    # 2. Setup current ready MUST tasks (to take up WIP)
    repo.ready_tasks = [Task(id="ready1", title="Ready1", category=TaskCategory.MUST, estimated_minutes=30)]

    # 3. Setup backlog tasks
    backlog_must = Task(
        id="b_must", title="Backlog Must", category=TaskCategory.MUST, estimated_minutes=30, energy_level="High"
    )
    backlog_should = Task(id="b_should", title="Backlog Should", category=TaskCategory.SHOULD, estimated_minutes=30)
    repo.backlog_tasks = [backlog_must, backlog_should]

    usecase = AutoAssignTasksUseCase(repo)
    target_date = date(2026, 8, 1)
    usecase.execute(target_date)

    assert len(repo.saved_tasks) == 3  # 1 past + 2 backlog (1 must, 1 should)

    assert past_task.target_date == target_date
    assert backlog_must.target_date == target_date
    assert backlog_should.target_date == target_date


def test_auto_assign_tasks_does_not_rollover_recurring_tasks():
    """
    定期タスク（RECURRING）は過去の未完了であっても翌日へロールオーバー（持ち越し）されないことを検証する。
    通常タスク（ONE_OFF）のみがロールオーバー対象となる。
    """
    repo = MockTaskRepositoryForAutoAssign()

    past_one_off = Task(
        id="past_one_off",
        title="Regular Task",
        category=TaskCategory.MUST,
        estimated_minutes=30,
        task_type=TaskType.ONE_OFF,
        target_date=date(2026, 7, 31),
    )
    past_recurring = Task(
        id="past_recurring",
        title="Weekend Chores",
        category=TaskCategory.SHOULD,
        estimated_minutes=30,
        task_type=TaskType.RECURRING,
        target_date=date(2026, 7, 31),
    )
    repo.past_tasks = [past_one_off, past_recurring]
    repo.ready_tasks = []
    repo.backlog_tasks = []

    usecase = AutoAssignTasksUseCase(repo)
    target_date = date(2026, 8, 1)
    usecase.execute(target_date)

    # ONE_OFFタスクは target_date に更新され保存される
    assert past_one_off.target_date == target_date
    assert past_one_off in repo.saved_tasks

    # RECURRINGタスクは持ち越されず、target_date も更新されず保存もされない
    assert past_recurring.target_date == date(2026, 7, 31)
    assert past_recurring not in repo.saved_tasks


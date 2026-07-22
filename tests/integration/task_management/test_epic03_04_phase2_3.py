import datetime
from typing import List

from integration.conftest import IntegrationTestContext

from application.task_management.daily_action_service import DailyActionService
from domain.task_management.repository import BriefingGateway, ScheduleGateway
from domain.task_management.task import Task, TaskCategory
from infrastructure.task_management.worklog_repository import SQLAlchemyWorklogRepository


class FakeScheduleGateway(ScheduleGateway):
    def sync_schedule(self, target_date: datetime.date, tasks: List[Task]) -> None:
        pass


class FakeBriefingGateway(BriefingGateway):
    def save(self, briefing) -> None:
        pass


def test_daily_action_service_plan_day_constraints(test_context: IntegrationTestContext):
    """[TM-PLAN-03]
    DailyActionService.plan_day の結合検証:
    1. リカバリー・ファースト制約（睡眠・Wantの確保）
    2. 15分バッファ制約
    3. Morning Deep Work 制約
    4. 未Readyタスク・孤立タスクの除外
    5. 視覚的強調(UX)とストック退避
    """
    task_repo = test_context.task_repo
    schedule_gateway = FakeScheduleGateway()
    briefing_repo = FakeBriefingGateway()
    worklog_repo = SQLAlchemyWorklogRepository(test_context.session)

    service = DailyActionService(
        task_repo=task_repo, schedule_gateway=schedule_gateway, briefing_repo=briefing_repo, worklog_repo=worklog_repo
    )

    target_date = datetime.date(2026, 7, 20)

    # 準備: テスト用のタスク群を作成
    tasks = [
        # 正常な Must タスク
        Task(
            id="task-1",
            title="Must Task 1",
            category=TaskCategory.MUST,
            estimated_minutes=60,
            area_id="01_Work",
            target_date=target_date,
        ),
        # Want タスク (1時間以上)
        Task(
            id="task-want",
            title="Important Want",
            category=TaskCategory.WANT,
            estimated_minutes=90,
            area_id="02_Life",
            target_date=target_date,
        ),
        # Morning Deep Work 対象
        Task(
            id="task-deep",
            title="Deep Work Task",
            category=TaskCategory.MUST,
            estimated_minutes=120,
            area_id="01_Work",
            target_date=target_date,
            energy_level="HIGH",
            is_deep_work=True,
        ),
        # 孤立タスク (area_id="00_Unknown")
        Task(
            id="task-isolated",
            title="Isolated Task",
            category=TaskCategory.SHOULD,
            estimated_minutes=30,
            area_id="00_Unknown",
            target_date=target_date,
        ),
        # 未Ready タスク (未完了の依存タスク task-999 がある)
        Task(
            id="task-unready",
            title="Unready Task",
            category=TaskCategory.MUST,
            estimated_minutes=30,
            area_id="01_Work",
            target_date=target_date,
            dependencies=["task-999"],
        ),
        # キャパシティオーバー用タスク (WIP制限や時間超過で退避される想定)
        Task(
            id="task-overflow",
            title="Overflow Task",
            category=TaskCategory.SHOULD,
            estimated_minutes=600,
            area_id="01_Work",
            target_date=target_date,
        ),
    ]
    task_repo.save_tasks(tasks)

    # 実行: スケジュール作成
    briefing = service.plan_day(target_date)

    # 検証 (Assert)

    scheduled_task_ids = [t.id for t in briefing.scheduled_tasks]

    # 4. 未Readyタスク・孤立タスクの除外
    assert "task-isolated" not in scheduled_task_ids, "孤立タスクはスケジュールから除外されるべき"
    assert "task-unready" not in scheduled_task_ids, "依存タスクが未完了のタスクは除外されるべき"

    # 1. リカバリー・ファースト制約: 睡眠ブロックの確保 (sleep というIDまたはタイトルの予定があること)
    #    及び 1時間以上の Want タスクが含まれていること
    assert any(
        "sleep" in getattr(t, "title", "").lower() or "睡眠" in getattr(t, "title", "")
        for t in briefing.scheduled_tasks
    ), "睡眠ブロックが確保されていること"
    assert "task-want" in scheduled_task_ids, "1時間以上のWantブロックが最優先で確保されていること"

    # 5. 視覚的強調(UX): Wantタスクの予定名に 👑 や 🛡️ などの絵文字が付与されていること
    want_task_scheduled = next((t for t in briefing.scheduled_tasks if t.id == "task-want"), None)
    assert want_task_scheduled is not None
    assert "👑" in want_task_scheduled.title or "🛡️" in want_task_scheduled.title, (
        "Wantタスクに視覚的強調の絵文字が付与されていること"
    )

    # 3. Morning Deep Work 制約: energy_level='High' のタスクは午前中 (start_time の時間が 12未満) に配置されること
    deep_task_scheduled = next((t for t in briefing.scheduled_tasks if t.id == "task-deep"), None)
    assert deep_task_scheduled is not None
    # Taskモデルに start_time 属性がない場合、ここで AttributeError になり Fail する
    assert hasattr(deep_task_scheduled, "start_time"), "タスクに開始時間 (start_time) が設定されていること"
    assert deep_task_scheduled.start_time.hour < 12, "High Energy タスクは午前中に配置されること"

    # 2. 15分バッファ制約: 連続するタスク間に15分の隙間があること
    sorted_tasks = sorted(
        [t for t in briefing.scheduled_tasks if hasattr(t, "start_time") and hasattr(t, "end_time")],
        key=lambda x: x.start_time,
    )
    for i in range(len(sorted_tasks) - 1):
        current_end = sorted_tasks[i].end_time
        next_start = sorted_tasks[i + 1].start_time
        buffer_delta = next_start - current_end
        assert buffer_delta >= datetime.timedelta(minutes=15), (
            "連続するタスク間には自動的に15分のバッファが確保されること"
        )

    # 5. ストック退避: 枠に収まりきらなかったタスクが棄却されず、deferred_tasks (または stock_tasks) に退避されていること
    assert hasattr(briefing, "deferred_tasks"), "DailyBriefingに退避タスク保持用属性(deferred_tasks)が存在すること"
    deferred_ids = [t.id for t in briefing.deferred_tasks]
    assert "task-overflow" in deferred_ids, "時間枠に収まらなかったタスクは棄却されず退避されること"

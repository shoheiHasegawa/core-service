from datetime import date, timedelta, datetime
from typing import List
import pytest

from domain.task_management.task import Task, TaskCategory, WarningFlag
from domain.task_management.planning_rules import (
    ContextBatchingPolicy,
    SchedulingValidator,
    WIPAllocationPolicy
)

# 以下のモジュール・クラスは未実装を想定（テスト実行時にImportErrorまたはAttributeErrorでFailする）
try:
    from domain.task_management.planning_rules import (
        DependencyPolicy,
        StrategicInvestmentPolicy,
        OrphanTaskPolicy,
        ScheduleBuilder,
        CircadianRhythmPolicy,
        MorningDeepWorkPolicy,
    )
except ImportError:
    pass

def create_task(id: str, category: TaskCategory, estimated_minutes: int, **kwargs) -> Task:
    return Task(
        id=id,
        title=f"Task {id}",
        category=category,
        estimated_minutes=estimated_minutes,
        **kwargs
    )

def test_task_04_deadline_exceeded_warning():
    """[TASK-04] LFD（限界期限）の超過警告"""
    yesterday = date.today() - timedelta(days=1)
    task = create_task("t1", TaskCategory.MUST, 30, deadline=yesterday)
    
    flags = SchedulingValidator.validate([task])
    assert WarningFlag.DEADLINE_EXCEEDED in flags

def test_task_05_context_switch_limit():
    """[TASK-05] コンテキストスイッチの超過: 深い⇔浅い作業の往復が最大3回以内に収まること"""
    # is_deep_work属性があると仮定
    tasks = []
    for i in range(10):
        t = create_task(f"t{i}", TaskCategory.MUST, 30)
        t.is_deep_work = (i % 2 == 0) # 交互に配置
        tasks.append(t)
    
    batched = ContextBatchingPolicy.apply(tasks)
    
    # 往復の回数を数える
    switches = 0
    for i in range(1, len(batched)):
        if batched[i].is_deep_work != batched[i-1].is_deep_work:
            switches += 1
            
    assert switches <= 3

def test_task_06_unready_task_invisible():
    """[TASK-06] 未Readyタスクの自動不可視化: 依存先タスクが未完了のタスクは完全に除外される"""
    task_a = create_task("t_a", TaskCategory.MUST, 30) # TODO state
    task_b = create_task("t_b", TaskCategory.MUST, 30, dependencies=["t_a"])
    
    # DependencyPolicy は未実装
    ready_tasks = DependencyPolicy.filter_ready([task_a, task_b], completed_task_ids=[])
    assert task_a in ready_tasks
    assert task_b not in ready_tasks

def test_task_07_strategic_investment_block():
    """[TASK-07] 戦略的投資枠の強制ブロック: 空き時間の20%が[S]タスクに強制ブロックされる"""
    s_task1 = create_task("s1", TaskCategory.SHOULD, 120)
    s_task2 = create_task("s2", TaskCategory.SHOULD, 60)
    
    # 10時間(600分)の空き時間の場合、20% = 120分が割り当てられるべき
    allocated = StrategicInvestmentPolicy.allocate(available_minutes=600, s_tasks=[s_task1, s_task2])
    
    total_allocated = sum(t.estimated_minutes for t in allocated)
    assert total_allocated >= 120

def test_task_08_orphan_task_exclusion():
    """[TASK-08] 孤立タスクの排除: 目的(Areas)に紐付いていないタスクは除外される"""
    task_valid = create_task("t1", TaskCategory.MUST, 30, area_id="Area_1")
    task_orphan1 = create_task("t2", TaskCategory.MUST, 30, area_id=None)
    task_orphan2 = create_task("t3", TaskCategory.MUST, 30, area_id="00_Unknown")
    
    filtered = OrphanTaskPolicy.filter([task_valid, task_orphan1, task_orphan2])
    assert task_valid in filtered
    assert task_orphan1 not in filtered
    assert task_orphan2 not in filtered

def test_task_09_deep_work_continuous_limit():
    """[TASK-09] ディープワーク連続稼働リミット到達: 90分で強制的にブレイク等が挿入されること"""
    task = create_task("t1", TaskCategory.MUST, 120)
    task.is_deep_work = True
    
    start_time = datetime(2026, 7, 19, 9, 0) # 09:00
    # ScheduleBuilder は未実装
    schedule = ScheduleBuilder.build(start_time, [task])
    
    # 09:00 - 10:30 (90分) -> Break/W (15~20分) -> 10:45 - 11:15 (30分)
    # scheduleの要素が { "task": Task/str, "start": datetime, "end": datetime } のような形だと仮定
    assert len(schedule) >= 3
    assert schedule[1]["task"].title in ["Break", "Low Energy", "W Task"]
    assert (schedule[1]["end"] - schedule[1]["start"]).total_seconds() / 60 >= 15

def test_task_10_circadian_dip_handling():
    """[TASK-10] サーカディアン・ディップの自動処理: 午後(13:00〜15:00)には[Energy: Low]または[W]のみ"""
    task = create_task("t1", TaskCategory.MUST, 60)
    task.is_deep_work = True # High Energyを想定
    
    # 13:30 に High Energy なタスクを配置しようとする
    schedule_item = {
        "task": task,
        "start": datetime(2026, 7, 19, 13, 30),
        "end": datetime(2026, 7, 19, 14, 30)
    }
    
    # エラーになるか False が返ることを期待
    is_valid = CircadianRhythmPolicy.validate([schedule_item])
    assert is_valid is False

def test_task_11_shutdown_ritual_fixed_placement():
    """[TASK-11] シャットダウン・リチュアルの固定配置: 最後の30分間は固定ブロック"""
    start_time = datetime(2026, 7, 19, 9, 0)
    end_time = datetime(2026, 7, 19, 18, 0)
    
    schedule = ScheduleBuilder.build_with_end(start_time, end_time, [])
    
    last_block = schedule[-1]
    assert last_block["task"].title == "Shutdown Ritual"
    assert (last_block["end"] - last_block["start"]).total_seconds() / 60 == 30
    assert last_block["end"] == end_time

def test_task_12_morning_shallow_work_error():
    """[TASK-12] 午前中の浅い作業ブロックエラー: 午前中の Shallow Work は拒絶される"""
    task = create_task("t1", TaskCategory.MUST, 60)
    task.is_deep_work = False # Shallow
    
    schedule_item = {
        "task": task,
        "start": datetime(2026, 7, 19, 10, 0),
        "end": datetime(2026, 7, 19, 11, 0)
    }
    
    is_valid = MorningDeepWorkPolicy.validate([schedule_item])
    assert is_valid is False

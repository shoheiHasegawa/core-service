"""
[TO-REG-01][TO-REF-01][TO-REF-02][TO-LIFE-01][TO-REG-02][TO-REG-03][TO-REF-03][TO-REF-04][TO-REF-05][TO-DOM-01]
Task Operations Integration Tests (6大観点マトリクス完全網羅)
"""

from datetime import date

import pytest
from integration.conftest import IntegrationTestContext
from sqlalchemy import text

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from domain.task_management.task import TaskCategory, TaskStatus, TaskType


def test_task_operations_lifecycle_integration(test_context: IntegrationTestContext):
    """
    [TO-REG-01] 正常系: タスクの新規登録 (Register Task)
    [TO-REF-01] 正常系: タスクのリファイン・部分更新 (Refine Task)
    [TO-LIFE-01] ライフサイクル: Register ➔ Refine ➔ Status Update がDB上で一貫して機能すること。
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    # 1. [TO-REG-01] 新規タスクの登録
    task = register_uc.execute(
        title="Lifecycle Integration Task",
        category=TaskCategory.MUST,
        estimated_minutes=45,
        reference_id="REF-100",
        task_type=TaskType.ONE_OFF,
        area_id="01_Work",
        last_memo="Initial plan memo",
    )

    assert task is not None
    assert task.title == "Lifecycle Integration Task"
    assert task.category == TaskCategory.MUST
    assert task.estimated_minutes == 45
    assert task.reference_id == "REF-100"
    assert task.area_id == "01_Work"
    assert task.last_memo == "Initial plan memo"
    assert task.status == TaskStatus.TODO

    # DB永続化の直接検証
    stmt = text("SELECT count(*) FROM tasks WHERE id = :id AND title = :title")
    count = test_context.session.execute(stmt, {"id": task.id, "title": "Lifecycle Integration Task"}).scalar()
    assert count == 1, "Task must be persisted in SQLite DB."

    # 2. [TO-REF-01] タスクのリファイン（タイトル変更、見積もり変更、期限設定、メモ追記）
    target_deadline = date(2026, 8, 10)
    refined_task = refine_uc.execute(
        task_id=task.id,
        title="Refined Lifecycle Task",
        estimated_minutes=60,
        deadline=target_deadline,
        last_memo="Refined updated memo",
    )

    assert refined_task is not None
    assert refined_task.id == task.id
    assert refined_task.title == "Refined Lifecycle Task"
    assert refined_task.estimated_minutes == 60
    assert refined_task.deadline == target_deadline
    assert refined_task.last_memo == "Refined updated memo"
    assert refined_task.category == TaskCategory.MUST  # 更新指定していないフィールドは維持されること

    # 3. [TO-LIFE-01] ステータス更新（完了への変更）
    completed_task = refine_uc.execute(
        task_id=task.id,
        status=TaskStatus.COMPLETED,
    )
    assert completed_task.status == TaskStatus.COMPLETED

    # DB内の最新状態を検証
    db_task = test_context.task_repo.get_tasks_by_ids([task.id])[0]
    assert db_task.status == TaskStatus.COMPLETED
    assert db_task.title == "Refined Lifecycle Task"
    assert db_task.estimated_minutes == 60


def test_refine_task_idempotency_integration(test_context: IntegrationTestContext):
    """
    [TO-REF-02] 冪等性: 同一パラメータで RefineTaskUseCase を複数回実行してもデータが破壊されず同一状態を保つこと。
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    task = register_uc.execute(title="Idempotent Task", estimated_minutes=30)

    # 1回目の更新
    first_run = refine_uc.execute(
        task_id=task.id,
        title="Updated Title",
        estimated_minutes=50,
        category=TaskCategory.WANT,
    )

    # 2回目の同一更新（冪等性）
    second_run = refine_uc.execute(
        task_id=task.id,
        title="Updated Title",
        estimated_minutes=50,
        category=TaskCategory.WANT,
    )

    assert first_run.title == second_run.title == "Updated Title"
    assert first_run.estimated_minutes == second_run.estimated_minutes == 50
    assert first_run.category == second_run.category == TaskCategory.WANT

    # DBのレコード数が増えていないこと（1件のまま）
    stmt = text("SELECT count(*) FROM tasks WHERE id = :id")
    count = test_context.session.execute(stmt, {"id": task.id}).scalar()
    assert count == 1


def test_register_task_boundary_validation_integration(test_context: IntegrationTestContext):
    """
    [TO-REG-02] 境界値: 空文字または空白のみのタイトルでの登録拒否 (ValueError)
    [TO-REG-03] 境界値: 0または負の見積もり時間での登録拒否 (ValueError)
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)

    # 空文字タイトル
    with pytest.raises(ValueError, match="Title must not be empty") as exc_info1:
        register_uc.execute(title="")
    assert "Title must not be empty" in str(exc_info1.value)

    # 空白のみのタイトル
    with pytest.raises(ValueError, match="Title must not be empty") as exc_info2:
        register_uc.execute(title="   ")
    assert "Title must not be empty" in str(exc_info2.value)

    # 見積もり時間 0
    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info3:
        register_uc.execute(title="Zero Min Task", estimated_minutes=0)
    assert "Estimated minutes must be positive" in str(exc_info3.value)

    # 見積もり時間 負数
    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info4:
        register_uc.execute(title="Negative Min Task", estimated_minutes=-10)
    assert "Estimated minutes must be positive" in str(exc_info4.value)


def test_refine_task_boundary_validation_integration(test_context: IntegrationTestContext):
    """
    [TO-REF-03] 境界値: Refine 時の空タイトルや不正な見積もり時間指定の拒否 (ValueError)
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    task = register_uc.execute(title="Valid Initial Task", estimated_minutes=30)

    # 空タイトルへの更新拒否
    with pytest.raises(ValueError, match="Title must not be empty") as exc_info1:
        refine_uc.execute(task_id=task.id, title="")
    assert "Title must not be empty" in str(exc_info1.value)

    with pytest.raises(ValueError, match="Title must not be empty") as exc_info2:
        refine_uc.execute(task_id=task.id, title="   ")
    assert "Title must not be empty" in str(exc_info2.value)

    # 不正な見積もり時間への更新拒否
    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info3:
        refine_uc.execute(task_id=task.id, estimated_minutes=0)
    assert "Estimated minutes must be positive" in str(exc_info3.value)

    with pytest.raises(ValueError, match="Estimated minutes must be positive") as exc_info4:
        refine_uc.execute(task_id=task.id, estimated_minutes=-5)
    assert "Estimated minutes must be positive" in str(exc_info4.value)


def test_refine_task_reconciliation_self_dependency_integration(test_context: IntegrationTestContext):
    """
    [TO-REF-04] 整合性: 自己依存（自身を dependencies に含む）の指定を拒否 (ValueError)
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    task = register_uc.execute(title="Self Dependency Task")

    with pytest.raises(ValueError, match="cannot depend on itself") as exc_info:
        refine_uc.execute(task_id=task.id, dependencies=[task.id])
    assert "cannot depend on itself" in str(exc_info.value)


def test_refine_task_fault_tolerance_not_found_integration(test_context: IntegrationTestContext):
    """
    [TO-REF-05] 異常系: 存在しない task_id に対する Refine 実行時に ValueError を送出すること。
    """
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    with pytest.raises(ValueError, match="not found") as exc_info:
        refine_uc.execute(task_id="non-existent-task-id-999", title="Ghost Update")
    assert "not found" in str(exc_info.value)


def test_task_operations_domain_invariants_integration(test_context: IntegrationTestContext):
    """
    [TO-DOM-01] ドメイン不変条件: 更新後も actual_minutes や cumulative_minutes が負数にならず不変条件が保たれること。
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    task = register_uc.execute(title="Invariant Task")
    assert task.actual_minutes >= 0
    assert task.cumulative_minutes >= 0

    refined = refine_uc.execute(task_id=task.id, estimated_minutes=120)
    assert refined.actual_minutes >= 0
    assert refined.cumulative_minutes >= 0

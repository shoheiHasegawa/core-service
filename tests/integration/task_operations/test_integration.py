"""[TO-REG-01][TO-REF-01][TO-REF-02] Task Operations Integration Tests"""

from integration.conftest import IntegrationTestContext
from sqlalchemy import text

from application.task_operations.refine_task_usecase import RefineTaskUseCase
from application.task_operations.register_task_usecase import RegisterTaskUseCase
from domain.task_management.task import TaskCategory, TaskType


def test_task_operations_lifecycle_integration(test_context: IntegrationTestContext):
    """
    [TO-REG-01] 正常系: タスクの新規登録 (Register Task)
    [TO-REF-01] 正常系: タスクのリファイン (Refine Task)
    SQLite DBを貫通させ、タスクの登録からDB永続化、およびリファインによる再取得・保存の一連の流れを検証する。
    """
    register_uc = RegisterTaskUseCase(task_repository=test_context.task_repo)
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)

    # 1. [TO-REG-01] 新規タスクの登録
    task = register_uc.execute(
        title="Integration Plan Task",
        description="Detailed description for integration",
        category=TaskCategory.MUST,
        estimated_minutes=45,
        reference_id="REF-100",
        task_type=TaskType.ONE_OFF,
    )

    assert task is not None
    assert task.title == "Integration Plan Task"
    assert task.category == TaskCategory.MUST
    assert task.estimated_minutes == 45
    assert task.reference_id == "REF-100"

    # DBに直接クエリして永続化されていることを確認
    stmt = text("SELECT count(*) FROM tasks WHERE id = :id AND title = :title")
    count = test_context.session.execute(stmt, {"id": task.id, "title": "Integration Plan Task"}).scalar()
    assert count == 1, "Task must be persisted in SQLite DB."

    # 2. [TO-REF-01] タスクのリファイン
    refined_task = refine_uc.execute(task.id)
    assert refined_task is not None
    assert refined_task.id == task.id
    assert refined_task.title == "Integration Plan Task"


def test_refine_task_not_found_integration(test_context: IntegrationTestContext):
    """
    [TO-REF-02] 異常系: 存在しないタスクのリファイン
    存在しないタスクIDを指定した際に安全に None が返却されることを検証する。
    """
    refine_uc = RefineTaskUseCase(task_repository=test_context.task_repo)
    result = refine_uc.execute("non-existent-task-id-999")
    assert result is None

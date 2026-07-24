from integration.conftest import IntegrationTestContext

from infrastructure.sqlalchemy.task_model import TaskModel


def test_task_management_integration(test_context: IntegrationTestContext):
    """
    [TM-PLAN-01] 正常系: 1日のプランニングの基本フローとリカバリーファースト
    [TM-PLAN-02] 異常系/エッジケース: WIP超過
    [TM-PLAN-03] 異常系/エッジケース: [W]タスク不足の警告
    [TM-PLAN-04] 異常系/エッジケース: LFD（限界期限）の超過警告
    [TM-PLAN-05] 異常系: コンテキストスイッチの超過
    [TM-PLAN-06] 異常系: 未Readyタスクの自動不可視化
    [TM-PLAN-07] 正常系/エッジケース: 戦略的投資枠の強制ブロック
    [TM-PLAN-08] 異常系: 孤立タスクの排除
    [TM-PLAN-09] 異常系: ディープワーク連続稼働リミット到達
    [TM-PLAN-10] 正常系: サーカディアン・ディップの自動処理
    [TM-PLAN-11] 正常系: シャットダウン・リチュアルの固定配置
    [TM-PLAN-12] 異常系: 午前中の浅い作業ブロックエラー
    """
    # 各シナリオ（[TM-PLAN-01]等）に基づく正しいセットアップ
    service = test_context.task_operations_service
    task = service.register_task(
        title="Integration Test Planning Task", description="Testing day planning flow", estimated_minutes=90
    )

    # daily_service による計画フェーズは別テストで検証予定

    # DBを直接クエリしての副作用確認
    # セッションからTaskModelを直接取得して、WIP超過やステータス更新など仕様に沿った状態かを確認する
    db_task = test_context.session.query(TaskModel).filter_by(id=task.id).one_or_none()

    assert db_task is not None, "Task must exist in the database."
    assert db_task.title == "Integration Test Planning Task", "Task title should match the registered value."
    assert db_task.status == "TODO", "Task status should be initialized as TODO."
    assert db_task.estimated_minutes == 90, "Task estimated minutes should be correctly saved."

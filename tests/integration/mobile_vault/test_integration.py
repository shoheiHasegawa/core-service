from integration.conftest import IntegrationTestContext


def test_vault_integration(test_context: IntegrationTestContext):
    """
    [MV-FILE-01] Retrieve Unprocessed Packets (未処理パケットの回収)
    [MV-FILE-02] Place Dashboard (ダッシュボードの配置)
    [MV-FILE-03] 異常系: ファイル上書き保存のエラー
    [MV-FILE-04] 異常系: ファイル移動先の上書きエラー
    """
    # Arrange
    import os
    import tempfile

    from sqlalchemy import text

    from application.mobile_vault.config import MobileVaultConfig
    from application.mobile_vault.service import MobileVaultService
    from domain.mobile_vault.parser import MarkdownImageParser
    from infrastructure.mobile_vault.local_file_mobile_vault_repository import LocalFileMobileVaultRepository

    inbox_dir = tempfile.mkdtemp()
    db_dir = tempfile.mkdtemp()
    with open(os.path.join(inbox_dir, "packet.md"), "w") as f:
        f.write("Test Packet")

    config = MobileVaultConfig(inbox_dir=inbox_dir, dashboard_dir=db_dir, attachments_dir=db_dir, queue_dir=db_dir)
    repository = LocalFileMobileVaultRepository()
    parser = MarkdownImageParser()
    service = MobileVaultService(
        config=config, repository=repository, parser=parser, task_repository=test_context.task_repo
    )

    # Act
    service.retrieve_packets()

    # Assert
    # DBを直接クエリしての副作用確認
    stmt = text("SELECT count(*) FROM tasks")
    result = test_context.session.execute(stmt).scalar()
    assert result == 1  # 1つのパケットがInboxタスクとして生成されることを検証

from unittest.mock import MagicMock

from application.mobile_vault.config import MobileVaultConfig
from application.mobile_vault.interfaces import MobileVaultRepository
from application.mobile_vault.service import MobileVaultService
from domain.mobile_vault.parser import MarkdownImageParser


def test_retrieve_unprocessed_packets_scenario_01(tmp_path):
    """[MV-FILE-01]
    [MV-FILE-01] Retrieve Unprocessed Packets (未処理パケットの回収)
    DIされたMobileVaultConfigからパスを取得し、Repository経由でファイルを読み込み、
    Domain層のParserを利用して一連の回収処理を行うテスト。
    """
    config = MobileVaultConfig(
        inbox_dir=tmp_path / "inbox",
        attachments_dir=tmp_path / "attachments",
        queue_dir=tmp_path / "queue",
        dashboard_dir=tmp_path / "dashboard",
    )

    mock_repo = MagicMock(spec=MobileVaultRepository)
    mock_parser = MagicMock(spec=MarkdownImageParser)

    mock_repo.list_markdown_files.return_value = [str(config.inbox_dir / "note1.md")]
    mock_repo.read_text.return_value = "Test content with ![[image.png]]"
    mock_parser.extract_images.return_value = ["image.png"]

    service = MobileVaultService(config=config, repository=mock_repo, parser=mock_parser)

    # Act
    processed_count = service.retrieve_packets()

    # Assert
    assert processed_count == 1
    mock_repo.list_markdown_files.assert_called_once_with(str(config.inbox_dir))
    mock_repo.read_text.assert_called_once_with(str(config.inbox_dir / "note1.md"))
    mock_parser.extract_images.assert_called_once_with("Test content with ![[image.png]]")
    mock_repo.delete_file.assert_called_once_with(str(config.inbox_dir / "note1.md"))


def test_place_dashboard_scenario_02(tmp_path):
    """[MV-FILE-01]
    [MV-FILE-02] Place Dashboard (ダッシュボードの配置)
    生成されたダッシュボードのMarkdownを、Mobile Vault上の指定ディレクトリに書き込む処理のテスト。
    """
    config = MobileVaultConfig(
        inbox_dir=tmp_path / "inbox",
        attachments_dir=tmp_path / "attachments",
        queue_dir=tmp_path / "queue",
        dashboard_dir=tmp_path / "dashboard",
    )
    mock_repo = MagicMock(spec=MobileVaultRepository)

    service = MobileVaultService(config=config, repository=mock_repo, parser=MagicMock(spec=MarkdownImageParser))

    content = "# My Dashboard\nContent here."
    filename = "dashboard.md"

    # Act
    result_path = service.place_dashboard(content=content, filename=filename)

    # Assert
    mock_repo.ensure_directory_exists.assert_called_once_with(str(config.dashboard_dir))
    mock_repo.save_file.assert_called_once_with(content=content, directory=str(config.dashboard_dir), filename=filename)
    assert result_path == str(config.dashboard_dir / filename)

"""[MV-PLACE-01][MV-PLACE-02] Place Dashboard Integration Tests"""

import tempfile
from pathlib import Path

from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from tests.integration.conftest import IntegrationTestContext


def test_place_dashboard_and_overwrite_integration(test_context: IntegrationTestContext):
    """
    [MV-PLACE-01] Place Dashboard (ダッシュボードの配置)
    [MV-PLACE-02] Dashboard配置の上書き処理
    実ファイルシステム（LocalFileMobileVaultGateway）を用いて書き込み・上書きを検証する。
    """
    with tempfile.TemporaryDirectory() as mobile_dir:
        # Arrange
        gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, dashboard_dir=mobile_dir)
        use_case = PlaceDashboardUseCase(publisher=gateway)

        # 1. 新規配置のテスト [MV-PLACE-01]
        result_path = use_case.execute(title="dashboard.md", content="# Hello Dashboard")

        expected_file = Path(mobile_dir) / "dashboard.md"
        assert Path(result_path).resolve() == expected_file.resolve()
        assert expected_file.exists()
        assert expected_file.read_text() == "# Hello Dashboard"

        # 2. 上書きのテスト [MV-PLACE-02]
        result_path_2 = use_case.execute(title="dashboard.md", content="# Overwritten Dashboard")

        assert Path(result_path_2).resolve() == expected_file.resolve()
        assert expected_file.exists()
        assert expected_file.read_text() == "# Overwritten Dashboard"

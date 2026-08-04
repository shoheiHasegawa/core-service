"""[MV-PLACE-01][MV-IDEM-02] Place Dashboard Integration Tests"""

import tempfile
from pathlib import Path

from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway
from tests.integration.conftest import IntegrationTestContext


def test_place_dashboard_new_file_integration(test_context: IntegrationTestContext):
    """
    [MV-PLACE-01] Place Dashboard (ダッシュボードの配置)
    PlaceDashboardUseCase により、指定されたタイトルとMarkdown内容がVaultへ正常に配置・保存され、
    配置先ファイルパスが返却されることを検証する。
    """
    with tempfile.TemporaryDirectory() as mobile_dir:
        # Arrange
        gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, dashboard_dir=mobile_dir)
        use_case = PlaceDashboardUseCase(publisher=gateway)

        # Act
        result_path = use_case.execute(title="Briefing_2026-08-04.md", content="# Daily Briefing\n- [ ] Task 1")

        # Assert
        expected_file = Path(mobile_dir) / "Briefing_2026-08-04.md"
        assert Path(result_path).resolve() == expected_file.resolve()
        assert expected_file.exists()
        assert expected_file.read_text(encoding="utf-8") == "# Daily Briefing\n- [ ] Task 1"


def test_place_dashboard_idempotency_overwrite_integration(test_context: IntegrationTestContext):
    """
    [MV-IDEM-02] Idempotent Place Dashboard (上書き・洗い替え)
    既に同名ファイルが存在する状態で PlaceDashboardUseCase を実行した場合、
    安全に洗い替え（完全上書き保存）され、ファイル重複や追記エラーが発生せず冪等であることを検証する。
    """
    with tempfile.TemporaryDirectory() as mobile_dir:
        # Arrange
        gateway = LocalFileMobileVaultGateway(inbox_dir=mobile_dir, dashboard_dir=mobile_dir)
        use_case = PlaceDashboardUseCase(publisher=gateway)

        # 1回目配置
        result_path_1 = use_case.execute(title="dashboard.md", content="# Initial Dashboard Content")
        expected_file = Path(mobile_dir) / "dashboard.md"
        assert Path(result_path_1).resolve() == expected_file.resolve()
        assert expected_file.read_text(encoding="utf-8") == "# Initial Dashboard Content"

        # 2回目配置（洗い替え・上書き）
        result_path_2 = use_case.execute(title="dashboard.md", content="# Overwritten Fresh Content")
        assert Path(result_path_2).resolve() == expected_file.resolve()
        assert expected_file.exists()
        assert expected_file.read_text(encoding="utf-8") == "# Overwritten Fresh Content"

        # ファイルが1つのみ存在すること（重複ファイルが生成されていないこと）
        all_files = list(Path(mobile_dir).glob("*.md"))
        assert len(all_files) == 1

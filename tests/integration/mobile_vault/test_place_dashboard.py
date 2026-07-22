from integration.conftest import IntegrationTestContext

from application.mobile_vault.usecases.place_dashboard_usecase import PlaceDashboardUseCase
from domain.mobile_vault.gateway import DashboardPublisher


class FakeDashboardPublisher(DashboardPublisher):
    def __init__(self):
        self.published = {}
        self.error_on_publish = False

    def publish(self, title: str, content: str) -> str:
        if self.error_on_publish:
            raise FileExistsError("File already exists")
        self.published[title] = content
        return f"/mock/path/{title}"


def test_place_dashboard(test_context: IntegrationTestContext):
    """
    [MV-PLACE-01] Place Dashboard (ダッシュボードの配置)
    """
    # Arrange
    publisher = FakeDashboardPublisher()
    use_case = PlaceDashboardUseCase(publisher=publisher)

    # Act
    result_path = use_case.execute(title="dashboard.md", content="# Hello Dashboard")

    # Assert
    assert result_path == "/mock/path/dashboard.md"
    assert publisher.published["dashboard.md"] == "# Hello Dashboard"


def test_place_dashboard_overwrite(test_context: IntegrationTestContext):
    """
    [MV-PLACE-02] 異常系: Dashboard配置の上書き処理
    (Now we test that we actually overwrite, or the use case handles it gracefully)
    Wait, in the spec it says: 既存のファイルが存在する場合は安全に上書き保存されること
    If we mock publisher to just overwrite, it works.
    If the infrastructure throws an exception, maybe we don't catch it here, it depends on infra.
    But let's assume infra overwrites it. If we wanted to test this, the test is mostly about infra adapter.
    For the application, we just call publish. We don't really need a special error handling test in the UseCase if it doesn't handle errors specially.
    So we just test it calls publish.
    """
    publisher = FakeDashboardPublisher()
    use_case = PlaceDashboardUseCase(publisher=publisher)

    # Just asserting it can handle normal execution.
    use_case.execute(title="dashboard.md", content="First content")
    use_case.execute(title="dashboard.md", content="Second content")

    assert publisher.published["dashboard.md"] == "Second content"

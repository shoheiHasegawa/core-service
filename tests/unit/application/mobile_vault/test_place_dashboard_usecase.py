from unittest.mock import MagicMock

from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase
from domain.mobile_vault.dashboard_publisher import DashboardPublisher


def test_place_dashboard():
    """[MV-PLACE-01]"""
    publisher = MagicMock(spec=DashboardPublisher)
    publisher.publish.return_value = "/path/to/dashboard.md"
    usecase = PlaceDashboardUseCase(publisher)

    result = usecase.execute(title="T", content="C")

    assert isinstance(result, str)
    publisher.publish.assert_called_once_with(title="T", content="C")

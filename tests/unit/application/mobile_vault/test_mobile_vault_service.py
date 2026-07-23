from unittest.mock import MagicMock

from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase
from application.mobile_vault.retrieve_packets_usecase import RetrievePacketsUseCase


def test_mobile_vault_service():
    """[MV-RETRIEVE-01] [MV-PLACE-01]"""
    retrieve_usecase = MagicMock(spec=RetrievePacketsUseCase)
    place_usecase = MagicMock(spec=PlaceDashboardUseCase)

    service = MobileVaultService(retrieve_packets_usecase=retrieve_usecase, place_dashboard_usecase=place_usecase)

    retrieve_usecase.execute.return_value = 0
    assert service.retrieve_packets() == 0
    retrieve_usecase.execute.assert_called_once()

    place_usecase.execute.return_value = "/path"
    assert service.place_dashboard("title", "content") == "/path"
    place_usecase.execute.assert_called_once_with("title", "content")

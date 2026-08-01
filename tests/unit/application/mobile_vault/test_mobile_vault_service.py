from unittest.mock import MagicMock

from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.peek_inbox_usecase import PeekInboxUseCase
from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase
from application.mobile_vault.process_inbox_item_usecase import ProcessInboxItemUseCase


def test_mobile_vault_service():
    """[MV-RECV-01] [MV-RECV-02] [MV-PLACE-01]"""
    peek_usecase = MagicMock(spec=PeekInboxUseCase)
    process_usecase = MagicMock(spec=ProcessInboxItemUseCase)
    place_usecase = MagicMock(spec=PlaceDashboardUseCase)

    service = MobileVaultService(
        peek_inbox_usecase=peek_usecase,
        process_inbox_item_usecase=process_usecase,
        place_dashboard_usecase=place_usecase,
    )

    peek_usecase.execute.return_value = [{"item_id": "test"}]
    assert service.peek_inbox() == [{"item_id": "test"}]
    peek_usecase.execute.assert_called_once()

    process_usecase.execute.return_value = True
    assert service.process_inbox_item(item_id="test", action="idea", title="title", tags=[], energy_level=None) is True
    process_usecase.execute.assert_called_once_with("test", "idea", "title", [], None)

    place_usecase.execute.return_value = "/path"
    assert service.place_dashboard("title", "content") == "/path"
    place_usecase.execute.assert_called_once_with("title", "content")

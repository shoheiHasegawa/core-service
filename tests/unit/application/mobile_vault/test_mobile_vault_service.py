from unittest.mock import MagicMock

from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.mobile_vault.peek_mobile_inbox_usecase import PeekMobileInboxUseCase
from application.mobile_vault.place_dashboard_usecase import PlaceDashboardUseCase
from application.mobile_vault.process_mobile_packet_usecase import ProcessMobilePacketUseCase


def test_mobile_vault_service():
    """[MV-RECV-01] [MV-RECV-02] [MV-PLACE-01]"""
    peek_usecase = MagicMock(spec=PeekMobileInboxUseCase)
    process_usecase = MagicMock(spec=ProcessMobilePacketUseCase)
    place_usecase = MagicMock(spec=PlaceDashboardUseCase)

    service = MobileVaultService(
        peek_inbox_usecase=peek_usecase, process_packet_usecase=process_usecase, place_dashboard_usecase=place_usecase
    )

    peek_usecase.execute.return_value = [{"packet_id": "test"}]
    assert service.peek_inbox() == [{"packet_id": "test"}]
    peek_usecase.execute.assert_called_once()

    process_usecase.execute.return_value = True
    assert service.process_packet(packet_id="test", action="idea", title="title", tags=[], energy_level=None) is True
    process_usecase.execute.assert_called_once_with("test", "idea", "title", [], None)

    place_usecase.execute.return_value = "/path"
    assert service.place_dashboard("title", "content") == "/path"
    place_usecase.execute.assert_called_once_with("title", "content")

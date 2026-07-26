import tempfile
from unittest.mock import MagicMock

import googleapiclient.discovery
from sqlalchemy.orm import Session

from application.daily_planning.daily_planning_service import DailyPlanningService
from application.mobile_vault.mobile_vault_service import MobileVaultService
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.task_operations_service import TaskOperationsService
from di.config import CoreServiceConfig
from di.container import CoreServiceContainer


def test_container_initialization_and_services(monkeypatch):
    """[TM-PLAN-01] CoreServiceContainerが正しく依存関係を解決し、各Facadeを生成できることを検証する"""
    monkeypatch.setattr(
        googleapiclient.discovery, "build", lambda *args, **kwargs: MagicMock(spec=["execute", "events"])
    )
    with tempfile.TemporaryDirectory() as temp_dir:
        config = CoreServiceConfig(
            google_calendar_id="test_cal_id",
            google_credentials_path="test_path",
            mobile_inbox_dir=f"{temp_dir}/mobile_inbox",
            mobile_dashboard_dir=f"{temp_dir}/mobile_dashboard",
            mobile_attachments_dir=f"{temp_dir}/mobile_attachments",
            sb_inbox_dir=f"{temp_dir}/sb_inbox",
            sb_sense_making_dir=f"{temp_dir}/sb_sense",
            sb_permanent_notes_dir=f"{temp_dir}/sb_perm",
            sb_attachments_dir=f"{temp_dir}/sb_attach",
            sb_inbox_template_path=f"{temp_dir}/sb_inbox_template",
            sb_sense_making_template_path=f"{temp_dir}/sb_sense_template",
            sb_permanent_note_template_path=f"{temp_dir}/sb_perm_template",
            sb_forbidden_patterns=["forbidden"],
            agent_queue_dir=f"{temp_dir}/agent_queue",
            db_path="sqlite:///:memory:",
        )

        mock_session = MagicMock(spec=Session)

        container = CoreServiceContainer(config, mock_session)

        # Verify we can fetch all services properly
        daily_planning = container.get_daily_planning_service()
        assert isinstance(daily_planning, DailyPlanningService)

        task_ops = container.get_task_operations_service()
        assert isinstance(task_ops, TaskOperationsService)

        second_brain = container.get_second_brain_service()
        assert isinstance(second_brain, SecondBrainService)

        mobile_vault = container.get_mobile_vault_service()
        assert isinstance(mobile_vault, MobileVaultService)

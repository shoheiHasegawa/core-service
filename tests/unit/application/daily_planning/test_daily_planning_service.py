from datetime import date
from unittest.mock import MagicMock

from application.daily_planning.daily_planning_service import DailyPlanningService
from application.daily_planning.plan_day_usecase import PlanDayUseCase
from application.daily_planning.record_worklogs_usecase import RecordWorklogsUseCase
from application.daily_planning.sync_worklogs_usecase import SyncWorklogsUseCase


def test_daily_planning_service():
    """[TM-SYNC-04]"""
    plan_usecase = MagicMock(spec=PlanDayUseCase)
    record_usecase = MagicMock(spec=RecordWorklogsUseCase)
    sync_usecase = MagicMock(spec=SyncWorklogsUseCase)

    service = DailyPlanningService(
        plan_day_usecase=plan_usecase, record_worklogs_usecase=record_usecase, sync_worklogs_usecase=sync_usecase
    )

    plan_usecase.execute.return_value = None
    assert service.plan_day(date.today()) is None
    plan_usecase.execute.assert_called_once()

    record_usecase.execute.return_value = None
    assert service.record_worklogs("date", {}) is None
    record_usecase.execute.assert_called_once()

    sync_usecase.execute.return_value = None
    assert service.sync_worklogs() is None
    sync_usecase.execute.assert_called_once()

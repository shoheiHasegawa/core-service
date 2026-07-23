class DailyPlanningService:
    """
    Facade for Daily Planning feature.
    Provides entry points for plan_day, record_worklogs, and sync_worklogs.
    Delegates actual logic to UseCases.
    """

    def __init__(self, plan_day_usecase, record_worklogs_usecase, sync_worklogs_usecase):
        self.plan_day_usecase = plan_day_usecase
        self.record_worklogs_usecase = record_worklogs_usecase
        self.sync_worklogs_usecase = sync_worklogs_usecase

    def plan_day(self, *args, **kwargs):
        return self.plan_day_usecase.execute(*args, **kwargs)

    def record_worklogs(self, *args, **kwargs):
        return self.record_worklogs_usecase.execute(*args, **kwargs)

    def sync_worklogs(self, *args, **kwargs):
        return self.sync_worklogs_usecase.execute(*args, **kwargs)

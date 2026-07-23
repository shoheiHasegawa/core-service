class TaskOperationsService:
    """
    Facade for Task Operations feature.
    Provides entry points for register_task and refine_task.
    Delegates actual logic to UseCases.
    """

    def __init__(self, register_task_usecase, refine_task_usecase):
        self.register_task_usecase = register_task_usecase
        self.refine_task_usecase = refine_task_usecase

    def register_task(self, *args, **kwargs):
        return self.register_task_usecase.execute(*args, **kwargs)

    def refine_task(self, *args, **kwargs):
        return self.refine_task_usecase.execute(*args, **kwargs)

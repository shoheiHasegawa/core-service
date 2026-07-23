from domain.mobile_vault.gateway import DashboardPublisher


class PlaceDashboardUseCase:
    def __init__(self, publisher: DashboardPublisher):
        self.publisher = publisher

    def execute(self, title: str, content: str) -> str:
        return self.publisher.publish(title=title, content=content)

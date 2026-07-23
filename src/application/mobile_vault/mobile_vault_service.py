class MobileVaultService:
    """
    Facade for Mobile Vault integration feature.
    Delegates actual logic to UseCases.
    """

    def __init__(self, retrieve_packets_usecase, place_dashboard_usecase):
        self.retrieve_packets_usecase = retrieve_packets_usecase
        self.place_dashboard_usecase = place_dashboard_usecase

    def retrieve_packets(self):
        return self.retrieve_packets_usecase.execute()

    def place_dashboard(self, title: str, content: str):
        return self.place_dashboard_usecase.execute(title, content)

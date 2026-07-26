class MobileVaultService:
    """
    Facade for Mobile Vault integration feature.
    Delegates actual logic to UseCases.
    """

    def __init__(self, peek_inbox_usecase, process_packet_usecase, place_dashboard_usecase):
        self.peek_inbox_usecase = peek_inbox_usecase
        self.process_packet_usecase = process_packet_usecase
        self.place_dashboard_usecase = place_dashboard_usecase

    def peek_inbox(self):
        return self.peek_inbox_usecase.execute()

    def process_packet(
        self, packet_id: str, action: str, title: str = "", tags: list[str] = None, energy_level: str = None
    ):
        return self.process_packet_usecase.execute(packet_id, action, title, tags, energy_level)

    def place_dashboard(self, title: str, content: str):
        return self.place_dashboard_usecase.execute(title, content)

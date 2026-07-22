from abc import ABC, abstractmethod


class MobileVaultGateway(ABC):
    @abstractmethod
    def list_markdown_files(self) -> list[str]:
        pass

    @abstractmethod
    def read_text(self, filename: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, filename: str) -> None:
        pass

    @abstractmethod
    def save_inbox_file(self, content: str, filename: str) -> None:
        pass

    @abstractmethod
    def save_dashboard_file(self, content: str, filename: str) -> None:
        pass

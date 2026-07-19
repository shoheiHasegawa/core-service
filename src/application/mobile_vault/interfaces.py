from abc import ABC, abstractmethod


class MobileVaultRepository(ABC):
    @abstractmethod
    def list_markdown_files(self, directory: str) -> list[str]:
        pass

    @abstractmethod
    def read_text(self, file_path: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def ensure_directory_exists(self, directory: str) -> None:
        pass

    @abstractmethod
    def save_file(self, content: str, directory: str, filename: str) -> None:
        pass

    @abstractmethod
    def move_file(self, source_path: str, dest_path: str) -> None:
        pass

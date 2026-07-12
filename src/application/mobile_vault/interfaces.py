from abc import ABC, abstractmethod
from pathlib import Path


class IMobileVaultRepository(ABC):
    @abstractmethod
    def list_markdown_files(self, directory: Path) -> list[Path]:
        pass

    @abstractmethod
    def read_text(self, file_path: Path) -> str:
        pass

    @abstractmethod
    def delete_file(self, file_path: Path) -> None:
        pass

    @abstractmethod
    def ensure_directory_exists(self, directory: Path) -> None:
        pass

    @abstractmethod
    def save_file(self, content: str, directory: Path, filename: str) -> None:
        pass

    @abstractmethod
    def move_file(self, source_path: Path, dest_path: Path) -> None:
        pass

import shutil
from pathlib import Path

from application.mobile_vault.interfaces import IMobileVaultRepository


class ICloudVaultRepository(IMobileVaultRepository):
    def list_markdown_files(self, directory: Path) -> list[Path]:
        if not directory.exists() or not directory.is_dir():
            return []
        return [p for p in directory.iterdir() if p.is_file() and p.suffix == ".md"]

    def read_text(self, file_path: Path) -> str:
        return file_path.read_text(encoding="utf-8")

    def delete_file(self, file_path: Path) -> None:
        if file_path.exists():
            file_path.unlink()

    def ensure_directory_exists(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)

    def save_file(self, content: str, directory: Path, filename: str) -> None:
        file_path = directory / filename
        file_path.write_text(content, encoding="utf-8")

    def move_file(self, source_path: Path, dest_path: Path) -> None:
        shutil.move(str(source_path), str(dest_path))

import shutil
from pathlib import Path

from application.mobile_vault.interfaces import IMobileVaultRepository


class ICloudVaultRepository(IMobileVaultRepository):
    def list_markdown_files(self, directory: str) -> list[str]:
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        return [str(p) for p in dir_path.iterdir() if p.is_file() and p.suffix == ".md"]

    def read_text(self, file_path: str) -> str:
        return Path(file_path).read_text(encoding="utf-8")

    def delete_file(self, file_path: str) -> None:
        p = Path(file_path)
        if p.exists():
            p.unlink()

    def ensure_directory_exists(self, directory: str) -> None:
        Path(directory).mkdir(parents=True, exist_ok=True)

    def save_file(self, content: str, directory: str, filename: str) -> None:
        dir_path = Path(directory).resolve()
        file_path = (dir_path / filename).resolve()
        if not file_path.is_relative_to(dir_path):
            raise ValueError("Path traversal detected")
        if file_path.exists():
            raise FileExistsError(f"File already exists: {file_path}")
        file_path.write_text(content, encoding="utf-8")

    def move_file(self, source_path: str, dest_path: str) -> None:
        if Path(dest_path).exists():
            raise FileExistsError(f"File already exists: {dest_path}")
        shutil.move(source_path, dest_path)

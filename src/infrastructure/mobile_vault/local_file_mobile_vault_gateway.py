from pathlib import Path

from application.mobile_vault.interfaces import MobileVaultGateway


class LocalFileMobileVaultGateway(MobileVaultGateway):
    def __init__(self, inbox_dir: str, dashboard_dir: str = ""):
        self.inbox_dir = Path(inbox_dir).resolve() if inbox_dir else Path().resolve()
        self.dashboard_dir = Path(dashboard_dir).resolve() if dashboard_dir else Path().resolve()
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        if dashboard_dir:
            self.dashboard_dir.mkdir(parents=True, exist_ok=True)

    def list_markdown_files(self) -> list[str]:
        if not self.inbox_dir.exists() or not self.inbox_dir.is_dir():
            return []
        return [p.name for p in self.inbox_dir.iterdir() if p.is_file() and p.suffix == ".md"]

    def read_text(self, filename: str) -> str:
        file_path = (self.inbox_dir / filename).resolve()
        if not file_path.is_relative_to(self.inbox_dir):
            raise ValueError("Path traversal detected")
        return file_path.read_text(encoding="utf-8")

    def delete_file(self, filename: str) -> None:
        file_path = (self.inbox_dir / filename).resolve()
        if not file_path.is_relative_to(self.inbox_dir):
            raise ValueError("Path traversal detected")
        if file_path.exists():
            file_path.unlink()

    def save_inbox_file(self, content: str, filename: str) -> None:
        file_path = (self.inbox_dir / filename).resolve()
        if not file_path.is_relative_to(self.inbox_dir):
            raise ValueError("Path traversal detected")
        file_path.write_text(content, encoding="utf-8")

    def save_dashboard_file(self, content: str, filename: str) -> None:
        file_path = (self.dashboard_dir / filename).resolve()
        if not file_path.is_relative_to(self.dashboard_dir):
            raise ValueError("Path traversal detected")
        file_path.write_text(content, encoding="utf-8")

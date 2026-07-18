from application.mobile_vault.config import MobileVaultConfig
from application.mobile_vault.interfaces import IMobileVaultRepository
from domain.mobile_vault.parser import MarkdownImageParser


class MobileVaultService:
    def __init__(self, config: MobileVaultConfig, repository: IMobileVaultRepository, parser: MarkdownImageParser):
        self.config = config
        self.repository = repository
        self.parser = parser

    def retrieve_packets(self) -> int:
        files = self.repository.list_markdown_files(str(self.config.inbox_dir))
        processed_count = 0
        for file_path in files:
            content = self.repository.read_text(file_path)
            self.parser.extract_images(content)
            self.repository.delete_file(file_path)
            processed_count += 1
        return processed_count

    def place_dashboard(self, content: str, filename: str) -> str:
        self.repository.ensure_directory_exists(str(self.config.dashboard_dir))
        self.repository.save_file(content=content, directory=str(self.config.dashboard_dir), filename=filename)
        return str(self.config.dashboard_dir / filename)

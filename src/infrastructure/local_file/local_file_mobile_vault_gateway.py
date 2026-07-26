from datetime import datetime, timedelta
from pathlib import Path

from domain.mobile_vault.dashboard_publisher import DashboardPublisher
from domain.mobile_vault.dashboard_reader import DashboardReader
from domain.mobile_vault.packet import Packet
from domain.mobile_vault.packet_receiver import PacketReceiver


class LocalFileMobileVaultGateway(PacketReceiver, DashboardPublisher, DashboardReader):
    def __init__(self, inbox_dir: str, dashboard_dir: str = "", attachments_dir: str = ""):
        self.inbox_dir = Path(inbox_dir).resolve() if inbox_dir else Path().resolve()
        self.dashboard_dir = Path(dashboard_dir).resolve() if dashboard_dir else Path().resolve()
        self.attachments_dir = Path(attachments_dir).resolve() if attachments_dir else Path().resolve()
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        if self.attachments_dir != Path().resolve():
            self.attachments_dir.mkdir(parents=True, exist_ok=True)
        if dashboard_dir:
            self.dashboard_dir.mkdir(parents=True, exist_ok=True)

    def fetch_unprocessed_packets(self) -> list[Packet]:
        if not self.inbox_dir.exists() or not self.inbox_dir.is_dir():
            return []
        packets = []
        for p in self.inbox_dir.iterdir():
            if p.is_file() and p.suffix == ".md":
                content = p.read_text(encoding="utf-8")
                # Use the filename as packet_id
                packets.append(Packet(packet_id=p.name, content=content, images=[]))
        return packets

    def get_packet(self, packet_id: str) -> Packet | None:
        file_path = (self.inbox_dir / packet_id).resolve()
        if not file_path.is_relative_to(self.inbox_dir):
            return None
        if file_path.exists() and file_path.is_file():
            content = file_path.read_text(encoding="utf-8")
            return Packet(packet_id=file_path.name, content=content, images=[])
        return None

    def delete_packet(self, packet: Packet) -> None:
        file_path = (self.inbox_dir / packet.packet_id).resolve()
        if not file_path.is_relative_to(self.inbox_dir):
            raise ValueError("ディレクトリトラバーサル攻撃を検知しました")
        if file_path.exists():
            file_path.unlink()

    def get_image_path(self, image_filename: str) -> str | None:
        file_path = (self.attachments_dir / image_filename).resolve()
        if not file_path.is_relative_to(self.attachments_dir):
            return None
        if file_path.exists() and file_path.is_file():
            return str(file_path)
        return None

    def delete_image(self, image_filename: str) -> None:
        file_path = (self.attachments_dir / image_filename).resolve()
        if not file_path.is_relative_to(self.attachments_dir):
            raise ValueError("ディレクトリトラバーサル攻撃を検知しました")
        if file_path.exists():
            file_path.unlink()

    def publish(self, title: str, content: str) -> str:
        file_path = (self.dashboard_dir / title).resolve()
        if not file_path.is_relative_to(self.dashboard_dir):
            raise ValueError("ディレクトリトラバーサル攻撃を検知しました")
        file_path.write_text(content, encoding="utf-8")
        return str(file_path)

    def get_recent_dashboards(self) -> list[str]:

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        target_filenames = [
            f"Briefing_{yesterday.strftime('%Y-%m-%d')}.md",
            f"Briefing_{today.strftime('%Y-%m-%d')}.md",
        ]

        contents = []
        if not self.dashboard_dir.exists() or not self.dashboard_dir.is_dir():
            return contents

        for filename in target_filenames:
            file_path = (self.dashboard_dir / filename).resolve()
            if file_path.exists() and file_path.is_file():
                contents.append(file_path.read_text(encoding="utf-8"))

        return contents

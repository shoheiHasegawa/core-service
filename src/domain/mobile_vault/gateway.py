from abc import ABC, abstractmethod

from domain.mobile_vault.packet import Packet


class PacketReceiver(ABC):
    @abstractmethod
    def fetch_unprocessed_packets(self) -> list[Packet]:
        pass

    @abstractmethod
    def delete_packet(self, packet: Packet) -> None:
        pass


class DashboardPublisher(ABC):
    @abstractmethod
    def publish(self, title: str, content: str) -> str:
        """
        ダッシュボードをVaultへ配置する。
        :param title: ファイル名や識別子となるタイトル
        :param content: マークダウン等の内容
        :return: 配置先のパスや識別子
        """
        pass


class DashboardReader(ABC):
    @abstractmethod
    def get_recent_dashboards(self) -> list[str]:
        """直近のダッシュボードのテキスト内容一覧を取得する"""
        pass

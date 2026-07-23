from abc import ABC, abstractmethod


class DashboardReader(ABC):
    @abstractmethod
    def get_recent_dashboards(self) -> list[str]:
        """直近のダッシュボードのテキスト内容一覧を取得する"""
        pass

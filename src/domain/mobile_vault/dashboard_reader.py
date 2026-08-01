from abc import ABC, abstractmethod
from typing import Optional


class DashboardReader(ABC):
    @abstractmethod
    def read_dashboard(self, filename: str) -> Optional[str]:
        """指定したファイル名のダッシュボードの内容を取得する"""
        pass

    @abstractmethod
    def delete_dashboard(self, filename: str) -> None:
        """指定したファイル名のダッシュボードを削除する"""
        pass

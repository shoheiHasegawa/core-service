from abc import ABC, abstractmethod
from typing import Optional


class DashboardReader(ABC):
    @abstractmethod
    def read_dashboard(self, filename: str) -> Optional[str]:
        """指定したファイル名のダッシュボードの内容を取得する"""
        pass

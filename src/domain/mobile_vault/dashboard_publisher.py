from abc import ABC, abstractmethod


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

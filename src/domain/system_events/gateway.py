from abc import ABC, abstractmethod


class SystemEventGateway(ABC):
    @abstractmethod
    def publish_error(self, job_name: str, error_details: str) -> None:
        """
        システムエラーイベントを発行し、エラーパケットをキューに通知する。

        Args:
            job_name (str): エラーが発生したジョブやスクリプトの名称 (例: generate_daily_briefing)
            error_details (str): エラーの詳細やスタックトレース
        """
        pass

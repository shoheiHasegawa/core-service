from abc import ABC, abstractmethod
from typing import List

from .task import DailyBriefing


class BriefingGateway(ABC):
    @abstractmethod
    def save(self, briefing: DailyBriefing) -> None:
        """生成されたDailyBriefing（1日の計画結果）を永続化する"""
        pass

    @abstractmethod
    def get_recent_briefing_contents(self) -> List[str]:
        """直近のダッシュボード（Briefing）のテキスト内容一覧を取得する"""
        pass

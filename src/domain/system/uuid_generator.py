from abc import ABC, abstractmethod


class UUIDGenerator(ABC):
    @abstractmethod
    def generate(self) -> str:
        """ユニークな識別子を生成する"""
        pass

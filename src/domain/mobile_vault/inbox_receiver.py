from abc import ABC, abstractmethod

from domain.mobile_vault.inbox_item import InboxItem


class InboxReceiver(ABC):
    @abstractmethod
    def fetch_unprocessed_items(self) -> list[InboxItem]:
        pass

    @abstractmethod
    def get_item(self, item_id: str) -> InboxItem | None:
        pass

    @abstractmethod
    def delete_item(self, inbox_item: InboxItem) -> None:
        pass

    @abstractmethod
    def get_image_path(self, image_filename: str) -> str | None:
        pass

    @abstractmethod
    def delete_image(self, image_filename: str) -> None:
        pass

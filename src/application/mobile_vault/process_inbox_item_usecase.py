import os

from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.task_operations_service import TaskOperationsService
from domain.mobile_vault.inbox_receiver import InboxReceiver
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.second_brain.repository import SecondBrainGateway
from domain.task_management.task import TaskCategory


class ProcessInboxItemUseCase:
    def __init__(
        self,
        receiver: InboxReceiver,
        second_brain_service: SecondBrainService,
        task_operations_service: TaskOperationsService,
        sb_gateway: SecondBrainGateway,
        sb_attachments_dir: str,
        parser: MarkdownImageParser,
    ):
        self.receiver = receiver
        self.second_brain_service = second_brain_service
        self.task_operations_service = task_operations_service
        self.sb_gateway = sb_gateway
        self.sb_attachments_dir = sb_attachments_dir
        self.parser = parser

    def execute(
        self,
        item_id: str,
        action: str,
        title: str = "",
        tags: list[str] | None = None,
        energy_level: str | None = None,
    ) -> bool:
        inbox_item = self.receiver.get_item(item_id)
        if not inbox_item:
            return False

        if action not in ("idea", "task", "delete"):
            raise ValueError(f"Invalid action: {action}. Expected 'idea', 'task', or 'delete'.")

        images = self.parser.extract_images(inbox_item.content)

        if action == "idea":
            dto = RegisterInboxNoteDto(title=title or item_id, content=inbox_item.content, tags=tags)
            self.second_brain_service.register_inbox_note(dto)
            self._copy_assets(images)
        elif action == "task":
            category = TaskCategory.MUST if energy_level == "High" else TaskCategory.SHOULD
            self.task_operations_service.register_task(
                title=title or item_id,
                description=inbox_item.content,
                category=category,
                estimated_minutes=30,
            )

        self.receiver.delete_item(inbox_item)
        self._cleanup_images(images)

        return True

    def _copy_assets(self, images: list[str]) -> None:
        for img in images:
            src_path = self.receiver.get_image_path(img)
            if src_path:
                dest_path = os.path.join(self.sb_attachments_dir, img)
                self.sb_gateway.copy_asset(src_path, dest_path)

    def _cleanup_images(self, images: list[str]) -> None:
        for img in images:
            try:
                self.receiver.delete_image(img)
            except ValueError:
                pass

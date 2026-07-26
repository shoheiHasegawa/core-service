import os

from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.second_brain_service import SecondBrainService
from application.task_operations.task_operations_service import TaskOperationsService
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.mobile_vault.packet_receiver import PacketReceiver
from domain.second_brain.repository import SecondBrainGateway
from domain.task_management.task import TaskCategory


class ProcessMobilePacketUseCase:
    def __init__(
        self,
        receiver: PacketReceiver,
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
        self, packet_id: str, action: str, title: str = "", tags: list[str] = None, energy_level: str = None
    ) -> bool:
        packet = self.receiver.get_packet(packet_id)
        if not packet:
            return False

        if action == "idea":
            dto = RegisterInboxNoteDto(title=title or packet_id, content=packet.content, tags=tags)
            self.second_brain_service.register_inbox_note(dto)

            images = self.parser.extract_images(packet.content)
            for img in images:
                src_path = self.receiver.get_image_path(img)
                if src_path:
                    dest_path = os.path.join(self.sb_attachments_dir, img)
                    self.sb_gateway.copy_asset(src_path, dest_path)

            self.receiver.delete_packet(packet)
            for img in images:
                try:
                    self.receiver.delete_image(img)
                except ValueError:
                    pass

        elif action == "task":
            category = TaskCategory.MUST if energy_level == "High" else TaskCategory.SHOULD

            self.task_operations_service.register_task(
                title=title or packet_id, description=packet.content, category=category, estimated_minutes=30
            )

            self.receiver.delete_packet(packet)
            images = self.parser.extract_images(packet.content)
            for img in images:
                try:
                    self.receiver.delete_image(img)
                except ValueError:
                    pass

        elif action == "delete":
            self.receiver.delete_packet(packet)
            images = self.parser.extract_images(packet.content)
            for img in images:
                try:
                    self.receiver.delete_image(img)
                except ValueError:
                    pass

        return True

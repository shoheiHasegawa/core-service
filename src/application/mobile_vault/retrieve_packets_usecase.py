import uuid
from typing import Optional

from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.mobile_vault.packet_receiver import PacketReceiver
from domain.task_management.task import Task, TaskCategory, TaskStatus, TaskType
from domain.task_management.task_repository import TaskRepository


class RetrievePacketsUseCase:
    def __init__(
        self,
        receiver: PacketReceiver,
        parser: MarkdownImageParser,
        task_repository: Optional[TaskRepository] = None,
    ):
        self.receiver = receiver
        self.parser = parser
        self.task_repository = task_repository

    def execute(self) -> int:
        packets = self.receiver.fetch_unprocessed_packets()
        processed_count = 0
        for packet in packets:
            self.parser.extract_images(packet.content)

            if self.task_repository:
                task = Task(
                    id=str(uuid.uuid4()),
                    title=f"Process Packet: {packet.packet_id}",
                    category=TaskCategory.MUST,
                    estimated_minutes=15,
                    task_type=TaskType.ONE_OFF,
                    status=TaskStatus.TODO,
                )
                self.task_repository.save(task)

            self.receiver.delete_packet(packet)
            processed_count += 1

        return processed_count

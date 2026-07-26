from typing import Dict, List

from domain.mobile_vault.markdown_image_parser import MarkdownImageParser
from domain.mobile_vault.packet_receiver import PacketReceiver


class PeekMobileInboxUseCase:
    def __init__(self, receiver: PacketReceiver, parser: MarkdownImageParser):
        self.receiver = receiver
        self.parser = parser

    def execute(self) -> List[Dict]:
        packets = self.receiver.fetch_unprocessed_packets()
        result = []
        for packet in packets:
            # パースして画像名を取得
            image_names = self.parser.extract_images(packet.content)
            # 存在する画像の絶対パスを取得
            valid_images = []
            for img in image_names:
                path = self.receiver.get_image_path(img)
                if path:
                    valid_images.append({"name": img, "path": path})

            result.append(
                {
                    "packet_id": packet.packet_id,
                    "content": packet.content,
                    "images": valid_images,
                }
            )
        return result

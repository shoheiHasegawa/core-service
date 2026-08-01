from typing import Dict, List

from domain.mobile_vault.inbox_receiver import InboxReceiver
from domain.mobile_vault.markdown_image_parser import MarkdownImageParser


class PeekInboxUseCase:
    def __init__(self, receiver: InboxReceiver, parser: MarkdownImageParser):
        self.receiver = receiver
        self.parser = parser

    def execute(self) -> List[Dict]:
        inbox_items = self.receiver.fetch_unprocessed_items()
        result = []
        for inbox_item in inbox_items:
            # パースして画像名を取得
            image_names = self.parser.extract_images(inbox_item.content)
            # 存在する画像の絶対パスを取得
            valid_images = []
            for img in image_names:
                path = self.receiver.get_image_path(img)
                if path:
                    valid_images.append({"name": img, "path": path})

            result.append(
                {
                    "item_id": inbox_item.item_id,
                    "content": inbox_item.content,
                    "images": valid_images,
                }
            )
        return result

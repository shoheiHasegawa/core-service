import datetime
import re
from typing import List


class ZettelkastenFormatter:
    def __init__(self, template: str):
        self.template = template

    def format(self, title: str, body: str, tags: List[str] = None, **kwargs) -> str:
        result = self.template
        # タイトルと本文
        result = result.replace("{{TITLE}}", title)
        result = result.replace("[タイトル]", title)
        result = result.replace("[Title]", title)
        result = result.replace("{{BODY}}", body).replace("{{body}}", body)

        # 任意のプレースホルダ（kwargs）
        for key, value in kwargs.items():
            if value is not None:
                result = result.replace(f"{{{{{key}}}}}", str(value))
                result = result.replace(f"{{{{{key.upper()}}}}}", str(value))

        # 日付 ({{date}})
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        result = result.replace("{{date}}", current_time)

        # タグ (tags: [])
        if tags:
            clean_tags = [t.lstrip("#") for t in tags if t]
            tags_str = ", ".join(clean_tags)
            result = result.replace("tags: []", f"tags: [{tags_str}]")

        return result

    def generate_filename(self, title: str) -> str:
        # 日本語を残すため、ファイル名に使えない文字だけを置換
        safe_title = re.sub(r'[/\\*?"<>|]+', "_", title).strip()
        return f"{safe_title}.md"

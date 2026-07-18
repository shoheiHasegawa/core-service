import glob
import os
from typing import List


class LocalFileRepository:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def save(self, file_path: str, content: str) -> None:
        full_path = os.path.join(self.base_path, file_path)
        os.makedirs(os.path.dirname(full_path) or self.base_path, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read(self, file_path: str) -> str:
        full_path = os.path.join(self.base_path, file_path)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def copy_asset(self, source_file: str, dest_path: str) -> str:
        full_dest = os.path.join(self.base_path, dest_path)
        os.makedirs(os.path.dirname(full_dest), exist_ok=True)
        with open(source_file, "rb") as src, open(full_dest, "wb") as dst:
            dst.write(src.read())
        return full_dest

    def search(self, query: str, extension: str) -> List[str]:
        results = []
        search_pattern = os.path.join(self.base_path, "**", f"*{extension}")
        for file_path in glob.glob(search_pattern, recursive=True):
            with open(file_path, "r", encoding="utf-8") as f:
                if query in f.read():
                    results.append(os.path.basename(file_path))
        return results

    def get_all_notes(self, extension: str) -> List[str]:
        results = []
        search_pattern = os.path.join(self.base_path, "**", f"*{extension}")
        for file_path in glob.glob(search_pattern, recursive=True):
            with open(file_path, "r", encoding="utf-8") as f:
                results.append(f.read())
        return results

    def generate_safe_filename(self, title: str) -> str:
        import re
        safe_title = re.sub(r'[/\\*?"<>|]+', "_", title).strip()
        return f"{safe_title}.md"

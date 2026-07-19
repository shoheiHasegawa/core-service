import glob
import os
from typing import List


class LocalFileSecondBrainRepository:
    def __init__(self, base_path: str):
        self.base_path = base_path

    def save(self, file_path: str, content: str) -> None:
        from pathlib import Path

        resolved_base = Path(self.base_path).resolve()
        resolved_full = Path(os.path.join(self.base_path, file_path)).resolve()
        if not resolved_full.is_relative_to(resolved_base):
            raise ValueError("Path traversal detected")
        if resolved_full.exists():
            raise FileExistsError(f"File already exists: {file_path}")

        full_path = str(resolved_full)
        os.makedirs(os.path.dirname(full_path) or self.base_path, exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

    def read(self, file_path: str) -> str:
        from pathlib import Path

        resolved_base = Path(self.base_path).resolve()
        resolved_full = Path(os.path.join(self.base_path, file_path)).resolve()
        if not resolved_full.is_relative_to(resolved_base):
            raise ValueError("Path traversal detected")

        full_path = str(resolved_full)
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()

    def copy_asset(self, source_file: str, dest_path: str) -> str:
        from pathlib import Path

        resolved_base = Path(self.base_path).resolve()
        resolved_dest = Path(os.path.join(self.base_path, dest_path)).resolve()
        if not resolved_dest.is_relative_to(resolved_base):
            raise ValueError("Path traversal detected")
        if resolved_dest.exists():
            raise FileExistsError(f"File already exists: {dest_path}")

        full_dest = str(resolved_dest)
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

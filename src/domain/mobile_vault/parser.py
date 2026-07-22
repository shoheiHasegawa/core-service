import re


class MarkdownImageParser:
    def extract_images(self, content: str) -> list[str]:
        images = []
        # Obsidian format: ![[image.png]]
        obsidian_pattern = re.compile(r"!\[\[(.*?)\]\]")
        images.extend(obsidian_pattern.findall(content))

        # Standard markdown format: ![alt text](sample.jpg)
        standard_pattern = re.compile(r"!\[.*?\]\((.*?)\)")
        images.extend(standard_pattern.findall(content))

        return images


class BriefingMarkdownParser:
    def parse_completed_task_ids(self, content: str) -> list[str]:
        ids = []
        for line in content.splitlines():
            if line.strip().startswith("- [x]"):
                match = re.search(r"<!--\s*id:\s*(.+?)\s*-->", line)
                if match:
                    ids.append(match.group(1).strip())
        return ids

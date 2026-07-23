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

import re
from typing import List, Tuple


class MarkdownParser:
    """
    生のMarkdown文字列から、YAML Frontmatterのキー一覧と本文中のリンク情報を抽出するInfrastructureコンポーネント。
    """

    def __init__(self, content: str):
        self.content = content

    def parse_frontmatter_keys(self) -> set[str]:
        """YAML Frontmatter内に存在するキー名の集合を返す"""
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", self.content, re.DOTALL)
        if not match:
            return set()

        frontmatter = match.group(1)
        keys_found = set()
        for line in frontmatter.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                key = line.split(":", 1)[0].strip()
                keys_found.add(key)
        return keys_found

    def parse_links_with_line_numbers(self) -> List[Tuple[int, str]]:
        """
        本文からすべてのリンク文字列を抽出し、(行番号(1-indexed), 行全体の文字列) のリストを返す
        （簡易的に、本文の各行をそのまま返すことでDomainモデル側で禁止パターンチェックを行わせる）
        """
        lines = self.content.split("\n")
        # Frontmatter部分をスキップするロジック（簡易）
        if self.content.startswith("---"):
            parts = self.content.split("---", 2)
            if len(parts) >= 3:
                # header lines count
                parts[1].count("\n") + 2

        return [(i + 1, line) for i, line in enumerate(lines)]

    def extract_tags_and_aliases(self) -> Tuple[List[str], List[str]]:
        """(簡易実装) Frontmatterから tags と aliases の文字列を含む行を抽出して返す"""
        tags = []
        aliases = []
        if "---" in self.content:
            frontmatter_lines = self.content.split("---")[1].split("\n")
            for line in frontmatter_lines:
                if line.startswith("tags:"):
                    tags.append(line)
                elif line.startswith("aliases:"):
                    aliases.append(line)
        return tags, aliases

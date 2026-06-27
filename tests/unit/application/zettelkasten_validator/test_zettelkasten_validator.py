import unittest

from domain.zettelkasten_note import ZettelkastenNote
from infrastructure.markdown_parser import MarkdownParser


class TestZettelkastenNote(unittest.TestCase):
    def _create_note(self, filename: str, content: str) -> ZettelkastenNote:
        parser = MarkdownParser(content)
        return ZettelkastenNote(
            filename=filename,
            frontmatter_keys=parser.parse_frontmatter_keys(),
            lines_with_number=parser.parse_links_with_line_numbers(),
        )

    def test_valid_note(self):
        """[SCENARIO-01] Zettelkastenノートの正常系バリデーション"""
        content = """---
id: 20260620170000
aliases: []
tags: [#concept/test]
created_at: 2026-06-20
updated_at: 2026-06-20
---
# Valid Note
## Connections
- [Support] [[Valid_Other_Note]]
"""
        note = self._create_note("Valid_Note.md", content)
        errors = note.validate(forbidden_patterns=["/Mock_Area", "/Mock_Project"])
        self.assertEqual(len(errors), 0)

    def test_missing_frontmatter(self):
        """[SCENARIO-02] YAMLフロントマターの欠落・必須キー不足の検知"""
        content = "# No frontmatter"
        note = self._create_note("Bad.md", content)
        errors = note.validate(forbidden_patterns=["/Mock_Area", "/Mock_Project"])
        self.assertTrue(any("Missing YAML frontmatter" in e.message for e in errors))

    def test_invalid_links(self):
        """[SCENARIO-03] 禁止ディレクトリへのアウトバウンドリンク検知"""
        content = """---
id: 123
aliases: []
tags: []
created_at: 2026-06-20
updated_at: 2026-06-20
---
# Invalid Links
[Link to Area](file:///Users/mock/path/Mock_Area/Marketing.md)
[Link to Project](../../Mock_Project/Proj.md)
"""
        note = self._create_note("Bad_Links.md", content)
        errors = note.validate(forbidden_patterns=["/Mock_Area", "/Mock_Project"])
        self.assertTrue(any("Forbidden outbound link" in e.message for e in errors))


if __name__ == "__main__":
    unittest.main()

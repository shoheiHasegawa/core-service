import unittest
from core_service.domain.zettelkasten_note import ZettelkastenNote, ValidationError

class TestZettelkastenNote(unittest.TestCase):
    def test_valid_note(self):
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
        note = ZettelkastenNote(filename="Valid_Note.md", content=content)
        errors = note.validate()
        self.assertEqual(len(errors), 0)

    def test_missing_frontmatter(self):
        content = "# No frontmatter"
        note = ZettelkastenNote(filename="Bad.md", content=content)
        errors = note.validate()
        self.assertTrue(any("Missing YAML frontmatter" in e.message for e in errors))

    def test_invalid_links(self):
        content = """---
id: 123
aliases: []
tags: []
created_at: 2026-06-20
updated_at: 2026-06-20
---
# Invalid Links
[Link to Area](file:///Users/shoheihasegawa/play_ground/second-brain/10_Areas/Marketing.md)
[Link to Project](../../10_Projects/Proj.md)
"""
        note = ZettelkastenNote(filename="Bad_Links.md", content=content)
        errors = note.validate()
        self.assertTrue(any("Forbidden outbound link" in e.message for e in errors))

if __name__ == '__main__':
    unittest.main()

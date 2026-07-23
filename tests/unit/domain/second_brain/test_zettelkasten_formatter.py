import datetime

from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter


def test_format_template():
    """[SB-INBOX-01] Auto-generated spec"""
    # Arrange
    template = "# {{TITLE}}\n\n{{BODY}}\n\n{{date}}"
    formatter = ZettelkastenFormatter(template=template)

    # Act
    test_time = datetime.datetime(2026, 7, 19, 12, 30)
    result = formatter.format(title="My Note", body="This is the content.", current_time=test_time)

    # Assert
    assert result == "# My Note\n\nThis is the content.\n\n2026-07-19 12:30"

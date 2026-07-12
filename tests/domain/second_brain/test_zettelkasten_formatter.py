from domain.second_brain.zettelkasten_formatter import ZettelkastenFormatter


def test_format_template():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    template = "# {{TITLE}}\n\n{{BODY}}"
    formatter = ZettelkastenFormatter(template=template)

    # Act
    result = formatter.format(title="My Note", body="This is the content.")

    # Assert
    assert result == "# My Note\n\nThis is the content."


def test_generate_filename():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    formatter = ZettelkastenFormatter(template="")

    # Act
    filename = formatter.generate_filename(title="My Note")

    # Assert
    assert filename == "My Note.md"
    assert filename.endswith(".md")

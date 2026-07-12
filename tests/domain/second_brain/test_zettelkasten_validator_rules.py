from domain.second_brain.zettelkasten_validator import ZettelkastenValidator


def test_validate_missing_id():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    validator = ZettelkastenValidator()
    content = "---\ntags: [test]\n---\n# Content"

    # Act
    is_valid, errors = validator.validate(content)

    # Assert
    assert is_valid is False
    assert any("Missing ID" in e for e in errors)


def test_validate_missing_tags():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    validator = ZettelkastenValidator()
    content = "---\nid: 1234567890\n---\n# Content"

    # Act
    is_valid, errors = validator.validate(content)

    # Assert
    assert is_valid is False
    assert any("Missing tags" in e for e in errors)


def test_validate_forbidden_links():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    validator = ZettelkastenValidator(forbidden_dirs=["/draft", "/temp"])
    content = "---\nid: 123\ntags: [test]\n---\nLink to [/draft/note.md](/draft/note.md)"

    # Act
    is_valid, errors = validator.validate(content)

    # Assert
    assert is_valid is False
    assert any("forbidden directory" in e for e in errors)


def test_validate_tag_format_invalid():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    validator = ZettelkastenValidator()
    # "テスト" is Japanese, "domain" lacks hierarchy, "Concept/Test" has uppercase
    content = "---\nid: 123\ntags: [テスト, domain, Concept/Test]\n---\n# Content"

    # Act
    is_valid, errors = validator.validate(content)

    # Assert
    assert is_valid is False
    # There should be format errors for each invalid tag
    assert any("Tag 'テスト' violates formatting rule" in e for e in errors)
    assert any("Tag 'domain' violates formatting rule" in e for e in errors)
    assert any("Tag 'Concept/Test' violates formatting rule" in e for e in errors)


def test_validate_tag_format_valid():
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    validator = ZettelkastenValidator()
    content = "---\nid: 123\ntags: [domain/machine_learning, concept/ai_orchestration]\n---\n# Content"

    # Act
    is_valid, errors = validator.validate(content)

    # Assert
    assert is_valid is True
    assert len(errors) == 0

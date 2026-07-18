import os

from infrastructure.second_brain.local_file_repository import LocalFileRepository


def test_save_and_read_note(tmp_path):
    """[SCENARIO-01]"""
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    repo = LocalFileRepository(base_path=str(tmp_path))
    note_content = "Test Note Content"
    file_path = "test_note.md"

    # Act
    repo.save(file_path, note_content)
    read_content = repo.read(file_path)

    # Assert
    assert read_content == note_content


def test_copy_asset(tmp_path):
    """[SCENARIO-01]"""
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    repo = LocalFileRepository(base_path=str(tmp_path))
    source_file = tmp_path / "source.png"
    source_file.write_bytes(b"image data")

    # Act
    dest_path = repo.copy_asset(str(source_file), "assets/dest.png")

    # Assert
    assert os.path.exists(dest_path)
    with open(dest_path, "rb") as f:
        assert f.read() == b"image data"


def test_search_existing_notes(tmp_path):
    """[SCENARIO-01]"""
    """[SCENARIO-01] Auto-generated spec"""
    # Arrange
    repo = LocalFileRepository(base_path=str(tmp_path))
    (tmp_path / "note1.md").write_text("Hello World")
    (tmp_path / "note2.md").write_text("Another Note")

    # Act
    results = repo.search("World", extension=".md")

    # Assert
    assert len(results) == 1
    assert "note1.md" in results[0]

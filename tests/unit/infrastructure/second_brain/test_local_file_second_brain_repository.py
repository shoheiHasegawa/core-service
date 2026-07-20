import os

from infrastructure.second_brain.local_file_second_brain_repository import LocalFileSecondBrainRepository


def test_save_and_read_note(tmp_path):
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    note_content = "Test Note Content"
    file_path = "test_note.md"

    # Act
    repo.save(file_path, note_content)
    read_content = repo.read(file_path)

    # Assert
    assert read_content == note_content


def test_copy_asset(tmp_path):
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    source_file = tmp_path / "source.png"
    source_file.write_bytes(b"image data")

    # Act
    dest_path = repo.copy_asset(str(source_file), "assets/dest.png")

    # Assert
    assert os.path.exists(dest_path)
    with open(dest_path, "rb") as f:
        assert f.read() == b"image data"


def test_search_existing_notes(tmp_path):
    """[SB-NOTE-01]"""
    """[SB-NOTE-01] Auto-generated spec"""
    # Arrange
    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    (tmp_path / "note1.md").write_text("Hello World")
    (tmp_path / "note2.md").write_text("Another Note")

    # Act
    results = repo.search("World", extension=".md")

    # Assert
    assert len(results) == 1
    assert "note1.md" in results[0]


def test_save_path_traversal(tmp_path):
    """[SB-NOTE-02] Path traversal attempt in save should raise ValueError"""
    import pytest

    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    with pytest.raises(ValueError, match="Path traversal detected") as exc_info:
        repo.save("../outside.md", "content")
    assert "Path traversal" in str(exc_info.value)


def test_save_file_exists(tmp_path):
    """[SB-NOTE-03] Saving to an existing file should raise FileExistsError"""
    import pytest

    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    file_path = "test.md"
    repo.save(file_path, "content")
    with pytest.raises(FileExistsError) as exc_info:
        repo.save(file_path, "new content")
    assert isinstance(exc_info.value, FileExistsError)


def test_read_path_traversal(tmp_path):
    """[SB-NOTE-04] Path traversal attempt in read should raise ValueError"""
    import pytest

    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    with pytest.raises(ValueError, match="Path traversal detected") as exc_info:
        repo.read("../outside.md")
    assert "Path traversal" in str(exc_info.value)


def test_copy_asset_path_traversal(tmp_path):
    """[SB-NOTE-05] Path traversal attempt in copy_asset should raise ValueError"""
    import pytest

    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    source_file = tmp_path / "source.png"
    source_file.write_bytes(b"data")
    with pytest.raises(ValueError, match="Path traversal detected") as exc_info:
        repo.copy_asset(str(source_file), "../outside.png")
    assert "Path traversal" in str(exc_info.value)


def test_copy_asset_file_exists(tmp_path):
    """[SB-NOTE-06] Copying to an existing file should raise FileExistsError"""
    import pytest

    repo = LocalFileSecondBrainRepository(base_path=str(tmp_path))
    source_file = tmp_path / "source.png"
    source_file.write_bytes(b"data")
    dest_path = "dest.png"
    repo.copy_asset(str(source_file), dest_path)
    with pytest.raises(FileExistsError) as exc_info:
        repo.copy_asset(str(source_file), dest_path)
    assert isinstance(exc_info.value, FileExistsError)

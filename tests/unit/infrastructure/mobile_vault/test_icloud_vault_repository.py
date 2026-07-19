# 未実装のため ImportError (Red) になる
from infrastructure.mobile_vault.icloud_vault_repository import ICloudVaultRepository


def test_icloud_repository_list_markdown_files(tmp_path):
    """[VAULT-01]
    指定ディレクトリ内の .md ファイル一覧を正しく取得できるかのテスト。
    """
    repo = ICloudVaultRepository()
    inbox_dir = tmp_path / "inbox"
    inbox_dir.mkdir()

    file1 = inbox_dir / "note1.md"
    file2 = inbox_dir / "note2.txt"
    file3 = inbox_dir / "note3.md"

    file1.touch()
    file2.touch()
    file3.touch()

    files = repo.list_markdown_files(str(inbox_dir))

    assert len(files) == 2
    assert str(file1) in files
    assert str(file3) in files
    assert str(file2) not in files


def test_icloud_repository_file_operations(tmp_path):
    """[VAULT-01]
    ファイルの読み書き、削除、ディレクトリ作成など純粋なファイルI/Oのテスト。
    """
    repo = ICloudVaultRepository()
    work_dir = tmp_path / "work"

    # ディレクトリ作成
    repo.ensure_directory_exists(str(work_dir))
    assert work_dir.exists()
    assert work_dir.is_dir()

    # ファイル保存
    content = "Hello, Mobile Vault!"
    filename = "test.md"
    repo.save_file(content=content, directory=str(work_dir), filename=filename)

    file_path = work_dir / filename
    assert file_path.exists()

    # ファイル読み込み
    read_content = repo.read_text(str(file_path))
    assert read_content == content

    # ファイル削除
    repo.delete_file(str(file_path))
    assert not file_path.exists()


def test_icloud_repository_move_file(tmp_path):
    """[VAULT-01]
    ファイルの移動テスト。
    """
    repo = ICloudVaultRepository()
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    source_file = source_dir / "move_me.md"
    source_file.write_text("Move this file")

    dest_file = dest_dir / "moved.md"

    repo.move_file(source_path=str(source_file), dest_path=str(dest_file))

    assert not source_file.exists()
    assert dest_file.exists()
    assert dest_file.read_text() == "Move this file"


def test_icloud_repository_save_file_path_traversal(tmp_path):
    """[VAULT-02] Path traversal in save_file should raise ValueError"""
    import pytest

    repo = ICloudVaultRepository()
    work_dir = tmp_path / "work"
    repo.ensure_directory_exists(str(work_dir))

    with pytest.raises(ValueError, match="Path traversal detected") as exc_info:
        repo.save_file("content", str(work_dir), "../outside.md")
    assert "Path traversal" in str(exc_info.value)


def test_icloud_repository_save_file_exists(tmp_path):
    """[VAULT-03] Saving to an existing file should raise FileExistsError"""
    import pytest

    repo = ICloudVaultRepository()
    work_dir = tmp_path / "work"
    repo.ensure_directory_exists(str(work_dir))

    filename = "test.md"
    repo.save_file("content", str(work_dir), filename)
    with pytest.raises(FileExistsError) as exc_info:
        repo.save_file("new content", str(work_dir), filename)
    assert isinstance(exc_info.value, FileExistsError)


def test_icloud_repository_move_file_exists(tmp_path):
    """[VAULT-04] Moving to an existing file should raise FileExistsError"""
    import pytest

    repo = ICloudVaultRepository()
    source_dir = tmp_path / "source"
    dest_dir = tmp_path / "dest"
    source_dir.mkdir()
    dest_dir.mkdir()

    source_file = source_dir / "move_me.md"
    source_file.write_text("Move this file")

    dest_file = dest_dir / "moved.md"
    dest_file.write_text("Existing file")

    with pytest.raises(FileExistsError) as exc_info:
        repo.move_file(source_path=str(source_file), dest_path=str(dest_file))
    assert isinstance(exc_info.value, FileExistsError)

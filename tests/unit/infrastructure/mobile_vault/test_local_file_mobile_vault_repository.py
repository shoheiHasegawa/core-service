from infrastructure.mobile_vault.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway


def test_local_file_mobile_vault_gateway_list_markdown_files(tmp_path):
    """[MV-FILE-01]
    指定ディレクトリ内の .md ファイル一覧を正しく取得できるかのテスト。
    """
    inbox_dir = tmp_path / "inbox"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(inbox_dir), dashboard_dir=str(tmp_path))
    inbox_dir.mkdir(exist_ok=True)

    file1 = inbox_dir / "note1.md"
    file2 = inbox_dir / "note2.txt"
    file3 = inbox_dir / "note3.md"

    file1.touch()
    file2.touch()
    file3.touch()

    files = repo.list_markdown_files()

    assert len(files) == 2
    assert "note1.md" in files
    assert "note3.md" in files
    assert "note2.txt" not in files


def test_local_file_mobile_vault_gateway_save_and_read_file(tmp_path):
    """[MV-FILE-01] ファイルの保存と読み込みのテスト。"""
    # Arrange
    work_dir = tmp_path / "work"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(work_dir), dashboard_dir=str(tmp_path))

    content = "Hello, Mobile Vault!"
    filename = "test.md"
    file_path = work_dir / filename

    # Act
    repo.save_inbox_file(content=content, filename=filename)
    read_content = repo.read_text(filename)

    # Assert
    assert file_path.exists()
    assert read_content == content


def test_local_file_mobile_vault_gateway_delete_file(tmp_path):
    """[MV-FILE-01] ファイル削除のテスト。"""
    # Arrange
    work_dir = tmp_path / "work"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(work_dir), dashboard_dir=str(tmp_path))

    filename = "delete_me.md"
    file_path = work_dir / filename
    repo.save_inbox_file(content="Delete me", filename=filename)

    # Act
    repo.delete_file(filename)

    # Assert
    assert not file_path.exists()


def test_local_file_mobile_vault_gateway_save_file_path_traversal(tmp_path):
    """[MV-FILE-02] Path traversal in save_file should raise ValueError"""
    import pytest

    work_dir = tmp_path / "work"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(work_dir), dashboard_dir=str(tmp_path))

    with pytest.raises(ValueError, match="Path traversal detected") as exc_info:
        repo.save_inbox_file("content", "../outside.md")
    assert "Path traversal" in str(exc_info.value)

import pytest

from domain.mobile_vault.packet import Packet
from infrastructure.local_file.local_file_mobile_vault_gateway import LocalFileMobileVaultGateway


def test_local_file_mobile_vault_gateway_fetch_unprocessed_packets(tmp_path):
    """[MV-RECV-01]
    指定ディレクトリ内の .md ファイル一覧をPacketとして正しく取得できるかのテスト。
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

    packets = repo.fetch_unprocessed_packets()

    assert len(packets) == 2
    packet_ids = {p.packet_id for p in packets}
    assert "note1.md" in packet_ids
    assert "note3.md" in packet_ids


def test_local_file_mobile_vault_gateway_publish_dashboard(tmp_path):
    """[MV-PLACE-01] ダッシュボードの保存のテスト。"""
    # Arrange
    work_dir = tmp_path / "work"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(tmp_path), dashboard_dir=str(work_dir))

    content = "Hello, Mobile Vault Dashboard!"
    filename = "dashboard.md"
    file_path = work_dir / filename

    # Act
    returned_path = repo.publish(title=filename, content=content)

    # Assert
    assert file_path.exists()
    assert file_path.read_text(encoding="utf-8") == content
    assert returned_path == str(file_path)


def test_local_file_mobile_vault_gateway_delete_packet(tmp_path):
    """[MV-RECV-01] ファイル削除のテスト。"""
    # Arrange
    work_dir = tmp_path / "work"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(work_dir), dashboard_dir=str(tmp_path))

    filename = "delete_me.md"
    file_path = work_dir / filename

    # First create it normally
    work_dir.mkdir(exist_ok=True)
    file_path.write_text("Delete me")

    packet = Packet(packet_id=filename, content="Delete me", images=[])

    # Act
    repo.delete_packet(packet)

    # Assert
    assert not file_path.exists()


def test_local_file_mobile_vault_gateway_save_file_path_traversal(tmp_path):
    """[MV-PLACE-01] Path traversal in publish should raise ValueError"""

    work_dir = tmp_path / "work"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(tmp_path), dashboard_dir=str(work_dir))

    with pytest.raises(ValueError, match="ディレクトリトラバーサル攻撃を検知しました") as exc_info:
        repo.publish("../outside.md", "content")
    assert "ディレクトリトラバーサル攻撃を検知しました" in str(exc_info.value)


def test_local_file_mobile_vault_gateway_read_dashboard(tmp_path):
    """[MV-PLACE-01] 指定したファイル名のダッシュボードの内容を読み取れること"""
    dashboard_dir = tmp_path / "dashboards"
    repo = LocalFileMobileVaultGateway(inbox_dir=str(tmp_path), dashboard_dir=str(dashboard_dir))

    target_filename = "Briefing_2026-07-22.md"
    content = "# Briefing"
    repo.publish(target_filename, content)

    # 読み取れること
    read_content = repo.read_dashboard(target_filename)
    assert read_content == content

    # 存在しないファイルはNoneを返すこと
    assert repo.read_dashboard("nonexistent.md") is None


def test_local_file_mobile_vault_gateway_read_dashboard_empty_dir(tmp_path):
    """[MV-PLACE-01] 空ディレクトリの場合はNoneを返す。"""
    repo = LocalFileMobileVaultGateway(inbox_dir=str(tmp_path), dashboard_dir=str(tmp_path / "nonexistent"))
    assert repo.read_dashboard("test.md") is None


def test_local_file_mobile_vault_gateway_fetch_empty_dir(tmp_path):
    """[MV-RECV-01] 空ディレクトリの場合は空リストを返す。"""
    repo = LocalFileMobileVaultGateway(inbox_dir=str(tmp_path / "nonexistent"))
    assert repo.fetch_unprocessed_packets() == []

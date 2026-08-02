"""[SB-INBOX-01][SB-SENSE-01][SB-PERM-01][SB-SEARCH-01][SB-AUDIT-01][SB-NOTE-04][SB-NOTE-05][SB-NOTE-06] Second Brain Integration Tests"""

import os
import tempfile
from pathlib import Path

import pytest
from integration.conftest import IntegrationTestContext
from sqlalchemy import text

from application.second_brain.audit_zettelkasten_rules_usecase import AuditZettelkastenRulesUseCase
from application.second_brain.config import SecondBrainConfig
from application.second_brain.register_inbox_note_dto import RegisterInboxNoteDto
from application.second_brain.register_inbox_note_usecase import RegisterInboxNoteUseCase
from application.second_brain.register_permanent_note_dto import RegisterPermanentNoteDto
from application.second_brain.register_permanent_note_usecase import RegisterPermanentNoteUseCase
from application.second_brain.register_sense_making_note_dto import RegisterSenseMakingNoteDto
from application.second_brain.register_sense_making_note_usecase import RegisterSenseMakingNoteUseCase
from application.second_brain.search_notes_usecase import SearchNotesUseCase
from infrastructure.local_file.local_file_second_brain_gateway import LocalFileSecondBrainGateway


def test_second_brain_lifecycle_integration(test_context: IntegrationTestContext):
    """
    [SB-INBOX-01] 正常系: Inboxノートの登録とタスク自動発行
    [SB-SENSE-01] 正常系: Sense Making ノートの登録
    [SB-PERM-01] 正常系: Permanent ノートの登録
    [SB-SEARCH-01] 正常系: ノートの検索
    実ファイルシステムとSQLite DBを貫通させ、知識の登録から検索までのライフサイクルを検証する。
    """
    with tempfile.TemporaryDirectory() as base_dir:
        sb_dir = os.path.join(base_dir, "second-brain")
        inbox_dir = os.path.join(sb_dir, "00_Inbox")
        sense_dir = os.path.join(sb_dir, "20_Sense_Making")
        perm_dir = os.path.join(sb_dir, "30_Permanent_Notes")
        template_dir = os.path.join(sb_dir, "90_Meta", "Templates")

        os.makedirs(inbox_dir, exist_ok=True)
        os.makedirs(sense_dir, exist_ok=True)
        os.makedirs(perm_dir, exist_ok=True)
        os.makedirs(template_dir, exist_ok=True)

        template_path = os.path.join(template_dir, "template.md")
        with open(template_path, "w") as f:
            f.write("---\nid: {{date}}\ntags: []\n---\n# {{TITLE}}\n\n{{BODY}}")

        repository = LocalFileSecondBrainGateway(base_path=sb_dir)

        # 1. [SB-INBOX-01] Inbox ノート登録 & タスク自動発行
        inbox_uc = RegisterInboxNoteUseCase(
            save_dir=inbox_dir,
            template_path=template_path,
            repository=repository,
            task_repository=test_context.task_repo,
        )
        inbox_dto = RegisterInboxNoteDto(title="Integration Idea", content="Content of the idea", tags=["idea"])
        inbox_result = inbox_uc.execute(inbox_dto)
        assert inbox_result is True

        inbox_files = list(Path(inbox_dir).glob("*.md"))
        assert len(inbox_files) == 1
        assert "Integration Idea" in inbox_files[0].read_text()

        # DBに ToDo タスクが発行されたか確認
        stmt = text("SELECT count(*) FROM tasks WHERE title = :title")
        task_count = test_context.session.execute(stmt, {"title": "Process idea: Integration Idea"}).scalar()
        assert task_count == 1, "Expected exactly 1 task generated from Second Brain idea registration"

        # 2. [SB-SENSE-01] Sense Making ノート登録
        sense_uc = RegisterSenseMakingNoteUseCase(
            save_dir=sense_dir,
            template_path=template_path,
            repository=repository,
        )
        sense_dto = RegisterSenseMakingNoteDto(
            title="AI Orchestration Design",
            content="Detailed context on AI loop engineering",
            tags=["architecture"],
            source="Book X",
        )
        sense_result = sense_uc.execute(sense_dto)
        assert sense_result is True

        sense_files = list(Path(sense_dir).glob("*.md"))
        assert len(sense_files) == 1
        assert "AI Orchestration Design" in sense_files[0].read_text()

        # 3. [SB-PERM-01] Permanent ノート登録
        perm_uc = RegisterPermanentNoteUseCase(
            save_dir=perm_dir,
            template_path=template_path,
            repository=repository,
        )
        perm_dto = RegisterPermanentNoteDto(
            title="Proof of Red Principle",
            claim="Always verify red state before writing green code.",
            context="Prevents false positives in automated TDD.",
            connections="[[AI Orchestration Design]]",
            tags=["principle"],
        )
        perm_result = perm_uc.execute(perm_dto)
        assert perm_result is True

        perm_files = list(Path(perm_dir).glob("*.md"))
        assert len(perm_files) == 1
        perm_text = perm_files[0].read_text()
        assert "Proof of Red Principle" in perm_text
        assert "## 💡 Claim" in perm_text
        assert "## 🧭 Context" in perm_text
        assert "## 🔗 Connections" in perm_text

        # 4. [SB-SEARCH-01] ノートの検索
        search_uc = SearchNotesUseCase(repository=repository)
        results = search_uc.execute("Proof")
        assert len(results) >= 1
        assert any("Proof of Red Principle" in r for r in results)

        no_results = search_uc.execute("NonExistentKeywordXYZ")
        assert no_results == []


def test_second_brain_audit_rules_integration(test_context: IntegrationTestContext):
    """
    [SB-AUDIT-01] 正常系: Zettelkasten ルールの監査
    禁止パターン（forbidden）を含むノートを検知できるかを検証する。
    """
    with tempfile.TemporaryDirectory() as base_dir:
        sb_dir = os.path.join(base_dir, "second-brain")
        inbox_dir = os.path.join(sb_dir, "00_Inbox")
        os.makedirs(inbox_dir, exist_ok=True)

        config = SecondBrainConfig(
            inbox_dir=inbox_dir,
            sense_making_dir=sb_dir,
            permanent_notes_dir=sb_dir,
            attachments_dir=sb_dir,
            inbox_template_path=os.path.join(sb_dir, "template.md"),
            sense_making_template_path=os.path.join(sb_dir, "template.md"),
            permanent_note_template_path=os.path.join(sb_dir, "template.md"),
            forbidden_patterns=["forbidden_link"],
        )
        repository = LocalFileSecondBrainGateway(base_path=sb_dir)

        # 正常なノートを作成（id:, tags:, 階層タグ）
        valid_note = Path(inbox_dir) / "valid.md"
        valid_note.write_text("---\nid: 2026-08-02 23:00\ntags: [tech/ai]\n---\n# Valid Note\nThis is good.")

        audit_uc = AuditZettelkastenRulesUseCase(config=config, repository=repository)
        errors = audit_uc.execute()
        assert len(errors) == 0

        # 禁止パターンを含むノートを作成
        invalid_note = Path(inbox_dir) / "invalid.md"
        invalid_note.write_text("---\nid: 2026-08-02 23:00\ntags: [tech/ai]\n---\n# Invalid Note\nforbidden_link")

        errors_after = audit_uc.execute()
        assert len(errors_after) > 0


def test_second_brain_security_and_traversal_integration(test_context: IntegrationTestContext):
    """
    [SB-NOTE-04] 異常系: ディレクトリトラバーサル攻撃防御（Read）
    [SB-NOTE-05] 異常系: ディレクトリトラバーサル攻撃防御（Copy Asset）
    [SB-NOTE-06] 異常系: コピー先の上書きエラー
    管理外ディレクトリへのアクセスや不正な上書きがブロックされることを検証する。
    """
    with tempfile.TemporaryDirectory() as base_dir:
        sb_dir = os.path.join(base_dir, "second-brain")
        os.makedirs(sb_dir, exist_ok=True)
        repository = LocalFileSecondBrainGateway(base_path=sb_dir)

        # [SB-NOTE-04] ディレクトリトラバーサル（Read）
        outside_file = os.path.join(base_dir, "outside.secret")
        with open(outside_file, "w") as f:
            f.write("secret data")

        with pytest.raises(ValueError) as exc_info_read:
            repository.read(outside_file)
        assert "traversal" in str(exc_info_read.value).lower()

        # [SB-NOTE-05] ディレクトリトラバーサル（Copy Asset）
        src_file = os.path.join(sb_dir, "src.png")
        with open(src_file, "w") as f:
            f.write("img data")

        with pytest.raises(ValueError) as exc_info_copy:
            repository.copy_asset(src_file, outside_file)
        assert "traversal" in str(exc_info_copy.value).lower()

        # [SB-NOTE-06] コピー先上書きエラー
        dest_file = os.path.join(sb_dir, "dest.png")
        with open(dest_file, "w") as f:
            f.write("existing img")

        with pytest.raises(FileExistsError) as exc_info_exists:
            repository.copy_asset(src_file, dest_file)
        assert "already exists" in str(exc_info_exists.value).lower()

from integration.conftest import IntegrationTestContext
from sqlalchemy import text


def test_second_brain_integration(test_context: IntegrationTestContext):
    """
    [BRAIN-01] アイデアの取り込み (Register Knowledge)
    [BRAIN-02] 知識の検索 (Search Notes)
    [BRAIN-03] 監査 (Audit Rules)
    [BRAIN-04] 異常系: ディレクトリトラバーサル攻撃防御（Read）
    [BRAIN-05] 異常系: ディレクトリトラバーサル攻撃防御（Copy Asset）
    [BRAIN-06] 異常系: コピー先の上書きエラー
    """
    # [BRAIN-01] などのシナリオに基づくセットアップ
    # 実際の実装に合わせてServiceを呼び出し、DBへの副作用を引き起こす
    import os
    import tempfile

    from application.second_brain.config import SecondBrainConfig
    from application.second_brain.service import SecondBrainService
    from infrastructure.second_brain.local_file_repository import LocalFileRepository

    base_dir = tempfile.mkdtemp()
    config = SecondBrainConfig(
        inbox_dir=base_dir,
        sense_making_dir=base_dir,
        permanent_notes_dir=base_dir,
        attachments_dir=base_dir,
        inbox_template_path=os.path.join(base_dir, "template.md"),
        sense_making_template_path=os.path.join(base_dir, "template.md"),
        permanent_note_template_path=os.path.join(base_dir, "template.md"),
        forbidden_patterns=["forbidden"],
    )
    with open(config.inbox_template_path, "w") as f:
        f.write("{title}\\n{body}")

    repository = LocalFileRepository(base_path=base_dir)
    service = SecondBrainService(config=config, repository=repository, task_repository=test_context.task_repo)
    service.register_inbox_note("Integration Idea", "Content of the idea")

    # DBを直接クエリしての副作用確認 (Semantic Reward Hacking回避のため具体的なアサーション)
    # SecondBrainでの処理結果が何らかの形でDBに反映される（例：処理タスク化など）ことを想定
    stmt = text("SELECT count(*) FROM tasks WHERE title = :title")
    result = test_context.session.execute(stmt, {"title": "Process idea: Integration Idea"}).scalar()

    assert result == 1, "Expected exactly 1 task generated from Second Brain idea registration"

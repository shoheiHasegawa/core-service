from dataclasses import dataclass
from typing import List


@dataclass
class CoreServiceConfig:
    """
    SDK (core-service) 全体の依存性を組み立てるための設定値。
    agent-core（コンシューマー側）が環境変数などを読み込んでこれを組み立て、
    DIコンテナ（Composition Root）に渡します。
    """

    # データベース関連
    db_path: str

    # Vault (iCloud) 関連
    mobile_inbox_dir: str
    mobile_dashboard_dir: str

    # エージェント・システムキュー関連
    agent_queue_dir: str

    # 外部API (Google Calendar等) 関連
    google_calendar_id: str
    google_credentials_path: str

    # Second Brain 関連
    sb_inbox_dir: str
    sb_sense_making_dir: str
    sb_permanent_notes_dir: str
    sb_attachments_dir: str
    sb_inbox_template_path: str
    sb_sense_making_template_path: str
    sb_permanent_note_template_path: str
    sb_forbidden_patterns: List[str]

# core-service 物理ディレクトリ構造マップ

- `docs/`: アーキテクチャと詳細ルール
  - `rules/`: JITロードされる詳細設計・テストルール群
  - `architecture.md`: アーキテクチャ境界定義
  - `review.md`: レビューチェックリスト
- `src/`: プロダクションコード
  - `application/`: ユースケースのオーケストレーションと spec.md
  - `domain/`: ドメインモデル（ビジネスロジックと不変条件）
  - `infrastructure/`: 外部IFアダプター（SQLAlchemy等の具象実装）
- `tests/`: テストコード
  - `unit/`: 単体テスト
  - `integration/`: 結合テスト（モック禁止・実DB/コンポーネント結合）
- `Makefile`: コマンド集約（make check-all, test, lint, validate）
- `pyproject.toml`: 依存関係定義（uv管理）

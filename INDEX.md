# core-service 物理ディレクトリ構造マップ

- `configs/` (設定ファイル群)
- `docs/`
  - `rules/` (JITロードされる詳細ルール群)
  - `architecture.md`
  - `review.md`
- `scripts/` (Linterや検証ツール群)
- `src/`
  - `application/` (ユースケースのオーケストレーションとspec.md)
  - `domain/` (ドメインモデル)
  - `infrastructure/` (外部IFのAdapter)
- `tests/`
  - `unit/` (各レイヤーの単体テスト)
  - `integration/` (モックを外部境界のみに絞った結合テスト)
- `.github/workflows/`

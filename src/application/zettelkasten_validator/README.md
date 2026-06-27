# Zettelkasten Validator

このコンポーネントは、`second-brain`（知識ライブラリ）に保存されている Markdown ノート（Zettelkasten）が、所定のフォーマット（YAML Frontmatterの必須キー、禁止リンク等）を満たしているかを検証する機能を提供します。

## 機能概要とデータフロー

1. **取得**: `IZettelkastenRepository` を通じて `second-brain` からノート一覧を取得する。
2. **検証**: 各ノートに対し、Domainモデル（`ZettelkastenNote`）の `validate()` を実行する。
3. **目的**: Zettelkastenルール（YAMLフロントマターの存在、許可されないリンクの禁止など）に違反しているノートを検出し、そのリストを上位の呼び出し元へ返却する。

## Agent駆動パッケージング (Feature-Driven)
このディレクトリは、AIエージェントが自律的にコンテキストを理解できるよう、以下の構成で自己完結しています。
- `README.md` (本ファイル): 機能の全体像
- `spec.md`: 実装が担保すべき具体的な仕様（シナリオ）
- `zettelkasten_service.py`: 実際のユースケース実装

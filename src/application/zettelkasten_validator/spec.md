# Zettelkasten Validator Specifications

SDD (Specification Driven Development) に基づき、Zettelkastenノートの検証ユースケースにおける仕様を定義する。

## [SCENARIO-01] Zettelkastenノートの正常系バリデーション
- **前提**: 必須YAMLフロントマターがすべて存在し、禁止リンクが含まれていないMarkdownノートをパースする。
- **結果**: 検証エラーがゼロ（空のリスト）として返却されること。

## [SCENARIO-02] YAMLフロントマターの欠落・必須キー不足の検知
- **前提**: `id`, `aliases`, `tags`, `created_at`, `updated_at` のいずれかのキーが不足している、またはYAMLフロントマター自体が存在しないMarkdownノートをパースする。
- **結果**: `ValidationError` が返却され、不足しているキー名や欠落の旨がメッセージに含まれていること。

## [SCENARIO-03] 禁止ディレクトリへのアウトバウンドリンク検知
- **前提**: 本文内に `/10_Areas/`, `/10_Projects/`, `/00_Inbox/`, `/20_Sense_Making/`, `/30_Resources/` 等へのリンクが含まれるノートをパースする。
- **結果**: `ValidationError` が返却され、どの禁止パターンのリンクが何行目で検知されたかがメッセージに含まれていること。

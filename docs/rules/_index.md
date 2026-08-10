# Execution Constraints Index (実行制約インデックス)

本ディレクトリ（`core-service/docs/rules/`）には、Agentがコーディングやテストを実行する際に遵守すべき具体的な「制約（Execution Constraints）」が配置されている。
**⚠️ 指示（Agent向け）**: 自身のタスクに必要な制約のみを以下のリストから検索・抽出し、JITロード（読み込み）すること。不要なルールを読み込むとコンテキスト汚染の原因となるため厳禁である。

## ルール一覧

### アーキテクチャと設計 (Architecture & Design)
- `ddd_guidelines.md`: DDD（ドメイン駆動設計）に基づく各層（Domain, Application, Infrastructure）の実装制約。
- `dependency_injection.md`: DI（依存性の注入）およびSOLID原則に関する実装制約。
- `context_engineering.md`: 1 Concept = 1 File の原則など、コンテキスト隔離のための制約。

### エラーハンドリング (Error Handling)
- `error/layer_matrix.md`: レイヤ別（CLI, UseCase, Domain, Infra等）の例外送出ルールと標準例外の活用制約。
- `error/custom_exception.md`: 独自例外（Custom Exception）を追加する際の厳格な判断基準。
- `error/testing_exceptions.md`: テストにおける例外のアサーション・検証ルール。

### テスト戦略 (Testing Strategy)
- `testing/tdd_protocol.md`: ダブルループTDD（Outer/Inner）の手順と、Linter（validate_sdd.py）によるハードゲート制約。
- `testing/unit_test.md`: Unitテスト（単体テスト）のファイル配置や粒度に関する制約。
- `testing/integration_test.md`: 結合テストの境界、テストヘルパーの実装ルール、および6大観点マトリクスの制約。

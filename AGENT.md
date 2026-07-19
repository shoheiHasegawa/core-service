# AGENT.md: core-service ローカルルール

ここは「情報システム部（工場）」である。このリポジトリ内で作業する際は、以下のローカルルールを最優先すること。

## <persona>
あなたは「堅牢なシステムを構築するソフトウェアエンジニア（Orchestrator）」である。
自らコードを書いてはならない。常にサブエージェント（Worker）を起動し、権限を分離してタスクを委譲せよ。

## <jit_routing>
詳細な設計ルールやテスト方針は、作業開始前に必ず以下のドキュメントからJITロード（動的読み込み）すること。
- **アーキテクチャ境界線**: `docs/architecture.md` （※本番ジョブの配置禁止ルール等）
- **DDDおよびSOLIDの制約**: `docs/rules/ddd_guidelines.md`
- **DIと命名規則 (Naming Conventions)**: `docs/rules/dependency_injection.md`
- **テスト方針とTDD分業プロトコル (Mock禁止等)**: `docs/rules/testing_strategy.md`
## 実行環境の制約 (Makefile / uv)
- 本リポジトリのパッケージ管理およびコマンド実行は **`uv`** に依存している。
- AIエージェントがコマンドを実行する際は、生コマンド（`pytest` 等）を直接叩かず、必ず **`make check-all`**, `make test`, `make lint` などの **Makefile** を経由すること。
## <rules>
1. **[完全な独立性]**: このリポジトリ内のコードは、特定の実行環境（BotフレームワークやCLI等）に依存してはならない。
2. **[副作用の排除]**: DBへの書き込みや外部APIコールなどの副作用は、Interface（Port）を定義するだけに留める（※これはドメイン層の原則であり、具象クラスの存在を否定するものではない）。
3. **[Service-Configパターン]**: すべては 上位の実行環境（Composition Root等） から Dependency Injection されることを前提とし、内部で具象クラスをインスタンス化しない。（詳細は `docs/rules/dependency_injection.md` を参照）。
4. **[インフラストラクチャの境界]**: DBやファイル読み書きなどの具象実装（アダプター）は `core-service/src/infrastructure/` に配置すること。`agent-core` 側には実装の実体を持たず、設定とDI（`factories/`）の呼び出しのみを行うこと。
5. **[ルールの遵守義務]**: 実装完了時は、必ず上記ガイドラインに基づく厳格なレビューと、`scripts/validate_sdd.py` による自動検証を通過させること。

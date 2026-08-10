# AGENT.md: core-service ワークスペースコンテキスト

このファイルは、このディレクトリ（空間）に降り立ったAgentが「自身の責務」と「目的」を自律的に判断するためのローカルルール（Layer 2）である。

## <domain_mission> (Mission / WHO)
`agent-core`の指示を堅牢な機能として具現化する、ステートレス工場の絶対的な品質管理者（Builder & QA）となること。自らコードを書いてはならず、常にサブエージェント（Worker）を起動してタスクを委譲せよ。

## <domain_vision> (Vision / WHAT)
ドメイン駆動設計（DDD）によって拡張性と独立性が担保された、You_Incの正本（Single Source of Truth）となるロジック基盤。

## <domain_value> (Value / HOW)
- **Loop Engineering**: Agentが最も確実に作業できる「SDD（仕様定義）」と「ダブルループTDD」のサイクルを例外なく遵守する。
- **Test as a Contract**: 実装の正しさは、推論ではなく「失敗するテスト（Red）」をパスさせることでのみ証明する。

## <jit_routing>
詳細な設計ルールやテスト方針は、作業開始前に必ず以下のドキュメントからJITロード（動的読み込み）すること。
- **アーキテクチャ境界線**: `docs/architecture.md` （※本番ジョブの配置禁止ルール等）
- **DDDおよびSOLIDの制約**: `docs/rules/ddd_guidelines.md`
- **DIと命名規則 (Naming Conventions)**: `docs/rules/dependency_injection.md`
- **テスト方針とTDD分業プロトコル (Mock禁止等)**: `docs/rules/testing_strategy.md`
## 実行環境の制約 (Makefile / uv)
- 本リポジトリのパッケージ管理およびコマンド実行は **`uv`** に依存している。
- AIエージェントがコマンドを実行する際は、生コマンド（`pytest` 等）を直接叩かず、必ず **`make check-all`**, `make test`, `make lint` などの **Makefile** を経由すること。
- **[ハードゲートへのルーティング]**: TDDプロセスやコードの変更・検証を伴う実装ループを回す際は、自己判断でテストを叩かず、`agent-core/tools/verify_loop_state.py` 等のシステム的ハードゲートを通して実行・遷移すること。

## <rules>
1. **[完全な独立性]**: このリポジトリ内のコードは、特定の実行環境（BotフレームワークやCLI等）に依存してはならない。
2. **[副作用の排除]**: DBへの書き込みや外部APIコールなどの副作用は、Interface（Port）を定義するだけに留める（※これはドメイン層の原則であり、具象クラスの存在を否定するものではない）。
3. **[Service-Configパターン]**: すべては 上位の実行環境（Composition Root等） から Dependency Injection されることを前提とし、内部で具象クラスをインスタンス化しない。（詳細は `docs/rules/dependency_injection.md` を参照）。
4. **[インフラストラクチャの境界]**: DBやファイル読み書きなどの具象実装（アダプター）は `core-service/src/infrastructure/` に配置すること。`agent-core` 側には実装の実体を持たず、設定とDI（`app_context.py`）の呼び出しのみを行うこと。
5. **[ルールの遵守義務]**: 実装完了時は、必ず上記ガイドラインに基づく厳格なレビューと、`make check-all`（`validate_sdd.py`）による自動検証を通過させること。
6. **[Why-First ゲートキーピング (要求の妥当性検証)]**: DDD/SOLIDに基づく実装（コードを書く作業）に入る前に、必ずユーザーの要求に対して「その機能は本当に必要か？」「コードを書かずに既存の仕組みで解決できないか？（YAGNI原則のメタ適用）」というメタ認知プロセスを挟み、妥当性の合意を得てからMakerプロセスへ移行すること。
7. **[イタチごっこと不整合の防止 (多重防衛線)]**: 実装前に「どのコードとドキュメント（SSOT）に影響が及ぶか」を事前分析（Impact Analysis）せよ。また、実装前には `global-alignment-reviewer`、実装後には `compliance-reviewer` によるダブルレビューを必ず通過させ、特に**「コードと関連ドキュメントの同時更新（Atomic Update）」**が行われているかを司法チェックの必須項目とせよ。

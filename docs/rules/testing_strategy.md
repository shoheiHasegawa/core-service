# Testing Strategy & TDD Protocol

`core-service` におけるテスト設計およびAIエージェントによるテスト駆動開発の絶対ルールを定義する。

## 1. SDD / TDD のトレーサビリティ
- **仕様IDの採番ルール**: `[ドメイン略称]-[機能群]-[連番]`（例: `[TM-PLAN-01]`, `[MV-RECV-01]`, `[SB-NOTE-01]`）という普遍的な命名規則を使用すること。Epic依存の命名は禁止。
- すべての実装は `src/application/*/spec.md` に定義されたユースケースシナリオに基づくこと。
- すべてのテストコードの関数DocString内には、必ず担保する仕様ID（例: `[TM-PLAN-01]`）を記載し、仕様とテストのトレーサビリティを強制する。
- （これらは `scripts/validate_sdd.py` のLinterによってCI/CD的に自動検知される）

## 2. Integration Test (結合テスト) の制約と責務
- `tests/integration/` は、**公開Service仕様（In-Out）を固定し、要求シナリオの100%を網羅する**ための防波堤（ハーネス）である。
- **配置**: `tests/integration/` 配下には、`application/` などのレイヤー階層は作らず、直接ドメイン名（機能名）のディレクトリ（例: `task_management/`）を配置すること。結合テストの起点は常に Application層（ユースケース）であるため、レイヤー分類は不要である。
- **境界とDB接続の厳格化**: テストの境界は「Application層からインフラ実体（DB等）まで」とする。システムの層間における**Mock（モック化）を一切禁止**する。とくに `unittest.mock` 等を用いてRepositoryやDB接続をモックすることは厳禁であり、**必ずテスト用DB（インメモリSQLite等）へ接続させること**。
- **許容されるMock (Fakeの注入)**: Mockが許されるのは、外部API通信のみとする。ただし、現在時刻やUUIDなどの非決定的な値については、DIコンテナ経由で `FakeClock` や `FakeUUIDGenerator` などのテスト用スタブを注入することを例外として許可する。

## 2.1. 悪質なハック（AIの怠慢）の禁止
自動テストを形骸化させる以下の行為は静的解析（Linter）によって厳しくブロックされる。
- **例外の握りつぶし禁止**: テストファイル内において、カバレッジを稼ぐためだけに `try...except ImportError` や `Exception` などを用いてエラーを握りつぶすことを禁止する。例外をテストしたい場合は必ず `pytest.raises(ExpectedException):` を用いること。
- **無秩序なMockの禁止**: Unitテストにおいてモックを使用する場合、生の `unittest.mock.Mock()` の使用を禁止する。存在しないメソッドを呼び出してもアサーションが通ってしまうため、必ず `spec=...` または `autospec=True` を持たせること。

## 2.5. Integration Test の Helper 実装ルール (共通の型)
- `tests/integration/helpers/` に、結合テスト専用の「共通の型」を配置することを義務化する。
  - **`IntegrationTestContext`**: `agent-core` の振る舞い（DI組み立て）を模倣し、テストDBの初期化や具象Repositoryの注入を担う「実行環境の型」。
    - ⚠️ **State Leakage（状態汚染）の防止**: テスト間のデータ汚染を防ぐため、`IntegrationTestContext` は各テスト終了時に必ず「トランザクションのロールバック」またはDBの初期化を行う責務を持つこと。
  - **`TestDataBuilder`**: テストデータを生成しDBに事前投入するための「データ生成の型」。

## 2.6. アサーションの空洞化防止
- AIがカバレッジ目標を達成するためだけに中身の無いテストを書くことを防ぐため、結合テストの最後には必ず「**DBを直接クエリして副作用（データ状態の変更）をアサーションすること**」を義務付ける。

## 2.7. 意味的妥当性 (Semantic Validation) の原則
- AST（静的解析）をすり抜けるためだけの無意味なアサーション（例: `assert True` や `assert result is not None`）を「Semantic Reward Hacking」とみなし固く禁ずる。
- アサーションは、必ず `spec.md` に記載された仕様（要件や事後条件）を**意味的・論理的に検証するもの**でなければならない。

## 2.8. ドメイン貧血の防止策（テストの配置）
- 過去のアンチパターン（ドメインモデルの貧血）は、「Service層のテストばかりを書き、Domainエンティティのテストを怠ったこと」が根本原因である。
- **必ずDomain層（エンティティやポリシー）に対する独立したUnitテスト（Inner Loop）を書くこと**。これにより、Implementer AgentがService層に全ての手続き的ロジックを詰め込むことを防ぐ。

## 3. Unit Test (単体テスト) の制約と配置ルール (Context Engineering)
- Unitテストは、ドメインモデルの詳細な境界値やエッジケース、パーサーの挙動、そして各UseCaseのロジック分岐を網羅するために記述する（インナーループの検証）。
- **1 Concept = 1 File の原則**: Unitテストのファイル名は、対象となる実装ファイル名に `test_` をプレフィックスとして付与した名称（例: `test_register_task_usecase.py`）にすること。
- **配置（ディレクトリの一致）**: Unitテストのディレクトリ構造は、実装コードの `src/` 配下の構造と完全に一致させること。（例: `src/application/task_operations/` のテストは `tests/unit/application/task_operations/` に配置する）。これにより、Context Engineering（変更時のコンテキストノイズの排除と発見容易性）をテストコードにも適用する。

## 4. Application層のアーキテクチャ制約 (Feature-Driven Packaging)
- `src/application/` 配下は、機能（Feature）ごとにディレクトリを分割すること。
- 各ディレクトリには、AIエージェントがコンテキストを自己完結できるよう、必ず以下の3点セットを配置すること。
  - `README.md`: 機能の概要とデータフロー図
  - `spec.md`: 実装が担保すべき仕様（シナリオ）
  - `*.py`: 実装コード
- （この制約は `scripts/validate_sdd.py` によって自動検証される）

## 5. スクリプト群 (`scripts/`) のテスト制約
- `scripts/` に配置された開発補助ツールやLinter等に対しても、品質担保のためにテストを書くこと。
- その場合のテストコードは、`tests/unit/scripts/` 配下に配置すること。

## 6. AI Pair Programming Protocol (Outside-in TDD)
  - エージェントがタスクを実行する際、確証バイアスを防ぐため、1体のAIがテストと実装を兼務してはならない。
  - **Testerフェーズ (仕様固定とエスカレーション)**: `Tester Agent` を起動し、Failするテストを作成させる（`src/` への書き込み禁止）。
    - ⚠️ **Outside-in TDDの強制**: Tester Agent は、必ず Outer Loop（`tests/integration/` の結合テスト）から書き始めること。ここで「テストが書けない（In-Outが不明確）」場合は、`spec.md` の仕様が粗い証拠である。**Agentが独断で仕様を決定してはならない。必ずユーザーにエスカレーション（質問・確認）し、意思決定を仰いでから `spec.md` を詳細化すること。**
    - ⚠️ **ドキュメントとの関係と要求ID (Traceability)**: 結合テスト用の独自仕様書は作成しない。必ず `src/application/*/spec.md` を正本とし、Integrationテストの各関数のDocStringにも必ず `[SCENARIO-XX]` という仕様IDを記載してトレーサビリティを担保すること。
  - **Implementer (Red -> Green) フェーズ**: `Engineer Agent` がテストをパスさせるための実装を行う。
  - **Refactor (Green -> Clean) フェーズ【重要】**: テストがパスした後、Implementer は**直ちに**自身でDDDとSOLID原則に基づくリファクタリングを行う。
  - **Unit Test (内部エッジケース検証)**: 実装詳細（ドメインモデル等のエッジケース、境界値、状態遷移）はUnit Testで網羅的に固める。Unit Testは内部実装検証が目的であるため、`spec.md`の全シナリオ網羅は必須ではない。
  - **Gate (関所の強制)**:
    - レビュー前に必ず `scripts/validate_sdd.py` を実行すること。Integration Testが `spec.md` の要求仕様IDを100%網羅していること、また全テストでFake IDが使用されていないことを機械的に証明しなければならない。
    - これを通過しない限り、レビューへの提出およびリファクタリング完了を認めない。
  - **Specialized Reviewフェーズ**: 複数の専門特化ペルソナ（QA Engineer、Domain Architect等）に分割して並列でレビューを実行させる。

## 6. テスト品質とエッジケース制約
- **カバレッジの絶対閾値**: `make test` 時のカバレッジは常に 90% 以上を維持しなければならない。下回る場合はCI/Linterレベルでブロックされる。
- **エッジケースの明文化義務**: `spec.md` には、正常系シナリオだけでなく、必ず「異常系およびエッジケース（Null、境界値、不正フォーマット等）」のシナリオを定義すること。

## 7. 防衛的AIレビューサイクル（ハルシネーション防衛）
AIエージェント同士の自動レビューサイクルが誤った方向に暴走（コード崩壊）するのを防ぐため、以下の安全装置を設ける。
1. **クリティカル・シンキング（盲従の禁止）**:
   - Implementer（実装者）は、レビュー指摘を受けた際、すぐにコードを修正してはならない。
   - 必ず「その指摘が `architecture.md` や `spec.md` の制約と矛盾していないか」を反証（セルフチェック）し、誤ったハルシネーション指摘であれば「仕様に反する」と却下すること。
2. **サーキットブレーカー（上限回数）**:
   - 指摘と修正のループは「最大2往復まで」とする。
   - 2往復を超えても解決しない場合、または「既存のアーキテクチャ根幹を揺るがす破壊的指摘」が出た場合は、AIの独断による修正を即時停止し、人間（ユーザー）にエスカレーションして判断を仰ぐこと。

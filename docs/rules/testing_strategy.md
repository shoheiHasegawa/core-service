# Testing Strategy & TDD Protocol

`core-service` におけるテスト設計およびAIエージェントによるテスト駆動開発の絶対ルールを定義する。

## 1. Linterによるアーキテクチャ制約の自動検証 (Hard Gates)
AIがカバレッジを稼ぐための「悪質なハック」や「トレーサビリティの欠落」を防ぐため、以下の項目は **`agent-core/tools/validate_sdd.py`** によって静的解析（ハードゲート）されます。

- **双方向トレーサビリティ**: `spec.md` の仕様IDと、テスト関数のDocString内のID（例: `[TM-PLAN-01]`）の完全一致（Fake IDの禁止）。
- **Mockの完全禁止**: 結合テストにおける `unittest.mock`, `@patch`, `mocker` などの使用禁止。
- **アサーションの空洞化防止**: `assert` のないテストや、意味のない例外握りつぶしの禁止。
- **Feature-Driven Packaging**: `src/application/*/` 配下の `README.md`, `spec.md`, `*.py` のセット配置検証。

⚠️ **Agentへの指示**: 上記のルールをプロンプトで暗記・意識する必要はありません。実装完了時は必ず `make check-all` を実行し、Linterが吐き出すエラーメッセージに従ってコードを修正してください（司法への移譲）。

## 2. Integration Test (結合テスト) の制約と責務
- `tests/integration/` は、**公開Service仕様（In-Out）を固定し、要求シナリオの100%を網羅する**ための防波堤（ハーネス）である。
- **配置**: `tests/integration/` 配下には、`application/` などのレイヤー階層は作らず、直接ドメイン名（機能名）のディレクトリ（例: `task_management/`）を配置すること。結合テストの起点は常に Application層（ユースケース）であるため、レイヤー分類は不要である。
- **境界とDB接続の厳格化**: テストの境界は「Application層からインフラ実体（DB等）まで」とする。システムの層間における**Mock（モック化）を一切禁止**し、必ずテスト用DB（インメモリSQLite等）へ接続させること。
- **テストの粒度とグルーピング基準 (Grouping Principle)**:
  - **ライフサイクル（一連のCRUDストーリー）**: ノート登録・検索・更新などの流れるような業務フローは、1つの統合テスト関数にまとめて効率的かつ高速に検証する。
  - **前提条件が異なる関心事（セキュリティ・異常系・独立監査）**: ディレクトリトラバーサル防御やルール違反監査など、前提や検証目的が独立しているものは別テスト関数に明確に分離する。
- **許容されるMock (Fakeの注入)**: Mockが許されるのは外部API通信のみ。現在時刻やUUIDなどの非決定的な値は、DIコンテナ経由で `FakeClock` などを注入すること。

## 2.5. Integration Test の Helper 実装ルール (共通の型)
- `tests/integration/helpers/` に、結合テスト専用の「共通の型」を配置することを義務化する。
  - **`IntegrationTestContext`**: `agent-core` の振る舞い（DI組み立て）を模倣し、テストDBの初期化や具象Repositoryの注入を担う「実行環境の型」。
    - ⚠️ **State Leakage（状態汚染）の防止**: 各テスト終了時に必ず「トランザクションのロールバック」またはDBの初期化を行う責務を持つこと。
  - **`TestDataBuilder`**: テストデータを生成しDBに事前投入するための「データ生成の型」。

## 3. Unit Test (単体テスト) の制約と配置ルール (Context Engineering)
- Unitテストは、ドメインモデルの詳細な境界値やエッジケース、パーサーの挙動、そして各UseCaseのロジック分岐を網羅するために記述する（インナーループの検証）。
- **1 Concept = 1 File の原則**: Unitテストのファイル名は、対象実装ファイル名に `test_` をプレフィックスとして付与すること。
- **配置（ディレクトリの一致）**: Unitテストのディレクトリ構造は、実装コードの `src/` 配下の構造と完全に一致させること。

## 4. ダブルループTDD（Double-Loop TDD）標準開発フロー

`core-service` におけるすべての新機能開発およびリファクタリングは、以下の **ダブルループTDD（Outside-In TDD）** に従って実行する。

```
[外側ループ (Outer Loop: 仕様・結合テスト)]
  Step 1: SDD Spec Design (sdd-spec-writer) -> spec.md 定義 (要求ID, I/O型)
  Step 2: Outer Red (tdd-red-coder) -> tests/integration/ に仕様テストを作成 (FAIL確認)
      │
      ▼
  [内側ループ (Inner Loop: ドメイン・実装・単体テスト)]
    Step 3a: Inner Red (tdd-green-refactorer) -> tests/unit/ にドメイン単体テスト作成 (必要時)
    Step 3b: Inner Green -> src/ にドメイン・UseCaseを最小実装
    Step 3c: Refactor -> クリーンアーキテクチャ・SOLID原則に従い整理 (Green維持)
      │
      ▼
  Step 4: Outer Green -> tests/integration/ の結合テストが全件 PASS することを確認
  Step 5: Quality Gate & Compliance (司法) -> validate_sdd.py (カバレッジ >= 90%, 要求ID一致)
```

### 各ステップの厳格な遷移条件
1. **Outer Red 成立条件**:
   - `tests/integration/` に `spec.md` の全要求IDを紐付けた結合テストが作成され、テスト実行が **FAIL（Red）** すること（構文エラーではなくアサーション失敗であること）。
2. **Inner Loop 開発基準**:
   - 複雑なビジネスルールや計算、エッジケースは `tests/unit/` で単体テストを書きながらドメインを肉付けする。
3. **Outer Green 達成基準**:
   - `pytest tests/integration/` および `pytest tests/unit/` が **すべて PASS（Exit 0）** すること。
4. **Quality Gate 通過基準**:
   - `agent-core/tools/validate_sdd.py`（カバレッジ >= 90%、Makefile完全性、要求ID双方向トレーサビリティ、Linter）がノーエラーで完全合格すること。

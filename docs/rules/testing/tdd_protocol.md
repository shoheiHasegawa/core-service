# TDD Protocol & Validation (ダブルループTDD標準開発フロー)

`core-service` におけるすべての新機能開発およびリファクタリングは、以下の **ダブルループTDD（Outside-In TDD）** に従って実行する。

## 1. ダブルループTDD フロー
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

## 2. 各ステップの厳格な遷移条件
1. **Outer Red 成立条件**:
   - `tests/integration/` に `spec.md` の全要求IDを紐付けた結合テストが作成され、テスト実行が **FAIL（Red）** すること（構文エラーではなくアサーション失敗であること）。
   - **バグ修正時の絶対ルール**: バグ修正においては、まずバグを100%再現する「失敗する結合テスト（Proof of Red）」を作成し、テストが正しく落ちることを証明してからでなければ、1行も実装コードを修正してはならない。
2. **Inner Loop 開発基準**:
   - 複雑なビジネスルールや計算、エッジケースは `tests/unit/` で単体テストを書きながらドメインを肉付けする。
3. **Outer Green 達成基準**:
   - `pytest tests/integration/` および `pytest tests/unit/` が **すべて PASS（Exit 0）** すること。
4. **Quality Gate 通過基準**:
   - `agent-core/tools/validate_sdd.py`（カバレッジ >= 90%、Makefile完全性、要求ID双方向トレーサビリティ、Linter）がノーエラーで完全合格すること。

## 3. Linterによるアーキテクチャ制約の自動検証 (Hard Gates)
AIがカバレッジを稼ぐための「悪質なハック」や「トレーサビリティの欠落」を防ぐため、以下の項目は **`agent-core/tools/validate_sdd.py`** によって静的解析（ハードゲート）されます。

- **双方向トレーサビリティ**: `spec.md` の仕様IDと、テスト関数のDocString内のID（例: `[TM-PLAN-01]`）の完全一致（Fake IDの禁止）。
- **Mockの完全禁止**: 結合テストにおける `unittest.mock`, `@patch`, `mocker` などの使用禁止。
- **アサーションの空洞化防止**: `assert` のないテストや、意味のない例外握りつぶしの禁止。
- **Feature-Driven Packaging**: `src/application/*/` 配下の `README.md`, `spec.md`, `*.py` のセット配置検証。

⚠️ **Agentへの指示**: 上記のルールをプロンプトで暗記・意識する必要はありません。実装完了時は必ず `make check-all` を実行し、Linterが吐き出すエラーメッセージに従ってコードを修正してください（司法への移譲）。

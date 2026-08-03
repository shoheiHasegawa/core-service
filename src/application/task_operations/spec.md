# Task Operations 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜタスク操作（Task Operations）を独立パッケージとして分離するのか**:
  - スケジューリング計算（`daily_planning`）から、純粋なタスクの新規登録（Register）と属性更新・洗練（Refine）を分離し、高凝集・疎結合を維持するため。
- **なぜ部分更新（Partial Update）を許容するのか**:
  - 夜の計画（`priority-planner`）やAgentの自律処理において、変更したい属性（見積もりや優先度のみ等）だけを安全に更新可能にするため。
- **なぜ存在しないタスク更新時に例外を送出（Fail-Fast）するのか**:
  - サイレントな失敗による不整合の隠蔽を防ぎ、タイポや不正なリクエストを即座に検知・遮断するため。
- **なぜ Python標準の ValueError で統一するのか**:
  - 不要な独自例外クラスの増殖を抑え、YAGNI原則に則りシンプルで堅牢なエラーハンドリングを維持するため。

---

## 2. Contract (I/O Types & Exceptions)

### UseCases
- **`RegisterTaskUseCase.execute(...) -> Task`**:
  - `title`: str (必須, 1文字以上の非空白文字列)
  - `category`: Optional[TaskCategory] = None (省略時: `TaskCategory.SHOULD`)
  - `estimated_minutes`: int = 30 (必須: 1以上の正の整数)
  - `deadline`: Optional[date] = None
  - `target_date`: Optional[date] = None
  - `task_type`: Optional[TaskType] = None (省略時: `TaskType.ONE_OFF`)
  - `area_id`: str = "00_Unknown"
  - `reference_id`: Optional[str] = None
  - `energy_level`: Optional[str] = None
  - `dependencies`: Optional[List[str]] = None
  - `last_memo`: Optional[str] = None

- **`RefineTaskUseCase.execute(...) -> Task`**:
  - `task_id`: str (必須)
  - `title`: Optional[str] = None (指定時: 1文字以上の非空白文字列)
  - `category`: Optional[TaskCategory] = None
  - `estimated_minutes`: Optional[int] = None (指定時: 1以上の正の整数)
  - `deadline`: Optional[date] = None
  - `target_date`: Optional[date] = None
  - `status`: Optional[TaskStatus] = None
  - `task_type`: Optional[TaskType] = None
  - `area_id`: Optional[str] = None
  - `energy_level`: Optional[str] = None
  - `dependencies`: Optional[List[str]] = None
  - `last_memo`: Optional[str] = None

### Exceptions
- **`ValueError`**:
  - タイトルが空文字または空白のみの場合
  - 見積もり時間が 0 または負の数の場合
  - 存在しない `task_id` に対して `RefineTaskUseCase` を実行した場合
  - 自己依存（自身の `task_id` を `dependencies` に含む）を指定した場合

---

## 3. Scenarios (6大テスト要求マトリクス)

### 正常系 (Happy Path)
- `[TO-REG-01]`: `RegisterTaskUseCase` により、指定された全属性またはデフォルト値を持つ新規タスクがDBに永続化され、生成されたTaskエンティティが返却されること。
- `[TO-REF-01]`: `RefineTaskUseCase` により、既存タスクの指定された属性（タイトル、見積もり、期限、カテゴリ、ステータス、メモ等）のみが正しく更新され、DBに永続化されたTaskエンティティが返却されること。

### 冪等性・ライフサイクル (Idempotency & Lifecycle)
- `[TO-REF-02]`: 同一パラメータで `RefineTaskUseCase` を複数回実行しても、状態が破壊されず同一の結果が返ること（冪等性）。
- `[TO-LIFE-01]`: タスクの登録（Register）➔ 洗練（Refine）➔ 完了状態変更（Status Update）の一連のライフサイクルがDB上で矛盾なく動作すること。

### 境界値・空データ (Boundary)
- `[TO-REG-02]`: 空文字または空白のみのタイトル（`""`, `"   "`）で登録を試みた場合、`ValueError` が送出されること。
- `[TO-REG-03]`: 見積もり時間に `0` または負の数を指定して登録を試みた場合、`ValueError` が送出されること。
- `[TO-REF-03]`: Refine 時、空タイトルや 0 以下の見積もり時間を指定した場合に更新が拒否され `ValueError` が送出されること。

### 整合性・調停 (Reconciliation)
- `[TO-REF-04]`: 自身の `task_id` を `dependencies` に含める自己依存を指定して Refine を試みた場合、不整合として `ValueError` が送出されること。

### 異常系・耐障害性 (Fault Tolerance)
- `[TO-REF-05]`: 存在しない `task_id` を指定して Refine を実行した場合、サイレントに完了せず `ValueError` が送出されること。

### ドメイン不変条件 (Domain Invariants)
- `[TO-DOM-01]`: タスクの `actual_minutes` や `cumulative_minutes` が常に 0 以上であり、更新によってドメイン不変条件が破壊されないこと。

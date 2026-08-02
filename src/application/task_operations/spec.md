# Task Operations 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜタスク操作（Task Operations）を独立パッケージとして分離するのか**:
  - 日次計画（`daily_planning`）のような複雑なスケジューリング計算から、純粋な「タスクの新規登録（Register）」および「タスクの詳細化・洗練（Refine）」という基本操作を分離し、高凝集・疎結合を維持するため。
- **なぜ `RefineTaskUseCase` を設けるのか**:
  - 単なるCRUD更新にとどまらず、将来的に「タスクの具体化・分割（サブタスク化）」「見積もり時間の再計算」「優先度や詳細メタデータの洗練」を行うビジネスロジックのエントリーポイントとするため。
- **なぜデフォルト値を設けるのか**:
  - カテゴリ（`TaskCategory.SHOULD`）や所要時間（`30分`）、タスク種別（`TaskType.ONE_OFF`）に安全なデフォルト値を与えることで、ユーザーや他機能（Second Brain等）からの最小限の引数でのタスク発行を容易にするため。

---

## 2. Contract (I/O Types & Exceptions)

### UseCases
- **`RegisterTaskUseCase.execute(title: str, description: str, category: Optional[TaskCategory] = None, estimated_minutes: int = 30, reference_id: Optional[str] = None, task_type: Optional[TaskType] = None) -> Task`**:
  - 引数に基づき新規 `Task` エンティティ（UUID自動採番）を生成し、`TaskRepository` を通じて永続化して返却する。
  - 省略時のデフォルト値:
    - `category`: `TaskCategory.SHOULD`
    - `estimated_minutes`: `30`
    - `task_type`: `TaskType.ONE_OFF`
- **`RefineTaskUseCase.execute(task_id: str) -> Optional[Task]`**:
  - `task_id` で指定されたタスクを `TaskRepository` から取得し、更新・再保存して返却する。
  - 対象タスクが存在しない場合は `None` を返却する。

---

## 3. Scenarios (テスト要求シナリオ)

### 正常系 (Happy Path)
- `[TO-REG-01]`: `RegisterTaskUseCase` により、指定された属性（またはデフォルト値）を持つ新規タスクがDBに永続化され、同一のTaskエンティティが返却されること。
- `[TO-REF-01]`: `RefineTaskUseCase` により、既存のタスクがIDで正しく取得され、更新保存された上で返却されること。

### 異常系 (Edge Cases)
- `[TO-REF-02]`: `RefineTaskUseCase` において、存在しない `task_id` を指定した場合に例外を送出せず安全に `None` が返却されること。

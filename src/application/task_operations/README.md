# Task Operations (Task Registration & Refinement Engine)

## 1. Context & Objective (背景と目的)
- **Why (なぜ必要なのか)**: 日次計画（`daily_planning`）のような複雑なスケジューリング計算から、純粋な「タスクの新規登録」および「タスクの詳細化・リファイン」という基本操作を分離し、高凝集・疎結合なアーキテクチャを維持するため。
- **What (何を実現するのか)**: 単発タスクの登録、デフォルト値（30分/SHOULD）の自動適用、およびタスクの再取得・洗練（Refine）を提供する軽量なタスク操作エンジン。

---

## 2. Architecture & Data Flow (アーキテクチャ)

```mermaid
graph TD
    TOS[TaskOperationsService]
    RegUC[RegisterTaskUseCase]
    RefUC[RefineTaskUseCase]
    TR[TaskRepository (SQLite)]

    TOS -->|新規登録委譲| RegUC
    TOS -->|リファイン委譲| RefUC
    RegUC -->|UUID採番 & 保存| TR
    RefUC -->|ID検索 & 再保存| TR
```

---

## 3. Routing & Navigation (関連ファイルへのポインタ)

当機能に関する主要なファイル群へのリンク（ポインタ）。開発やテストを行う際は以下を参照すること。

- **仕様書 (Contract & Scenarios)**: [spec.md](./spec.md)
- **エントリーポイント (Facade / UseCases)**:
  - Facade: [task_operations_service.py](./task_operations_service.py)
  - 新規登録: [register_task_usecase.py](./register_task_usecase.py)
  - リファイン: [refine_task_usecase.py](./refine_task_usecase.py)
- **結合テスト (Integration Tests)**:
  - ライフサイクル＆異常系: `tests/integration/task_operations/test_integration.py`
- **単体テスト (Unit Tests)**:
  - Application: `tests/unit/application/task_operations/`

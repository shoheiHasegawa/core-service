# Daily Planning (Action & Reflection Pipeline)

## 1. Context & Objective (背景と目的)
- **Why (なぜ必要なのか)**: 社長（ユーザー）の認知負荷をゼロにし、意志力や気合に頼らず「必然的に成長し、かつ精神的に摩耗しない1日のタイムライン」を数学的・客観的に構築するため。
- **What (何を実現するのか)**: 内部DB（タスク・ルーティン）と外部SoR（Google Calendar）を統合し、生体リズム・心理的免罪符・WIP制限に基づくスケジューリング、カレンダーへの一方向Reconciliation同期、およびMobile Vaultへのブリーフィング配信と実績回収（Leave No Trace）を担うステートレスな計算エンジン。

---

## 2. Architecture & Data Flow (アーキテクチャ)

```mermaid
graph TD
    DPS[DailyPlanningService]
    Reg[(Task / Recurring Repositories)]
    GCal[Google Calendar Gateway]
    Vault[Mobile Vault Gateway]
    DB[(SQLite SoR)]

    DPS -->|1. 未完了タスク・ルーティン読み込み| Reg
    DPS -->|2. 外部予定取得 & 祝日/有休判定| GCal
    DPS -->|3. 9大制約に基づくスケジュール計算| DPS
    DPS -->|4. 一方向完全洗い替え (Reconciliation)| GCal
    DPS -->|5. Briefing_YYYY-MM-DD.md 配信| Vault
    DPS -->|6. 実績回収 & 完了更新 & 物理自動削除| DB
```

### アーキテクチャ上の責務
1. **純粋な計算エンジン**: 対話やセッション状態を持たず、与えられた日付の制約パズルを解いて `DailyBriefing` を出力する。
2. **SoR分離の担保**: 外部予定（会議・終日イベント）はカレンダーをRead-Onlyで参照し、内部タスク・ルーティンはDBを正本（Write）として一方向同期する。
3. **異常警告の委譲**: `[W]` 比率不足や期限超過などの異常は `warning_flags` として返却し、意思決定は上位のAgentic OS（秘書スキル）に委譲する。

---

## 3. Routing & Navigation (関連ファイルへのポインタ)

当機能に関する主要なファイル群へのリンク（ポインタ）。開発やテストを行う際は以下を参照すること。

- **仕様書 (Contract & Scenarios)**: [spec.md](./spec.md)
- **エントリーポイント (Facade / UseCases)**:
  - Facade: [daily_planning_service.py](./daily_planning_service.py)
  - 計画生成 & 同期: [plan_day_usecase.py](./plan_day_usecase.py)
  - 実績回収: [sync_worklogs_usecase.py](./sync_worklogs_usecase.py)
  - タスク自動アサイン: [auto_assign_tasks_usecase.py](./auto_assign_tasks_usecase.py)
- **結合テスト (Integration Tests)**:
  - `tests/integration/task_management/`
- **単体テスト (Unit Tests)**:
  - Application: `tests/unit/application/daily_planning/`
  - Domain: `tests/unit/domain/task_management/`
  - Infrastructure:
    - Google Calendar: `tests/unit/infrastructure/google_api/test_google_calendar_gateway.py`
    - SQLite Repositories: `tests/unit/infrastructure/sqlalchemy/`
    - Mobile Vault: `tests/unit/infrastructure/local_file/test_local_file_mobile_vault_gateway.py`

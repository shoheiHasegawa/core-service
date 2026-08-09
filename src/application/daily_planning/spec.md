# Daily Planning 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜリカバリーファースト・9大制約なのか**:
  - ストイックな個体の「休めない病」を解消するため、`[W] Want` 枠を先取り不可侵枠（`👑`）として配置し、`[S] Should` の進捗を論理的に証明することで心理的免罪符（Safety Pass）を提供する。
  - サーカディアンリズム（午前ディープ・午後ディップ）と超日リズム（90分限界）に従い、意志力の消耗を防ぐ。
- **なぜSoR分離（GCal=外部 / SQLite=内部）なのか**:
  - 双方向CRUDの競合やゴースト予定を根絶するため、外部予定（会議等）はカレンダーをRead-Onlyで参照し、内部タスク・ルーティンはDBを正本（Write）として一方向Reconciliation（完全洗い替え）を行う。
  - 終日予定は時間をブロックするのではなく、「日のコンテキストを修飾するメタデータ（例: 有休/祝日）」として解釈する。
- **なぜLeave No Trace（物理自動削除）なのか**:
  - ファイルシステムをステート（状態）として残すと同期漏れやゴーストファイルが発生するため、実績回収完了後は `Briefing_YYYY-MM-DD.md` を即時物理削除し、DBのみを永続SoRとする。

---

## 2. Contract (I/O Types)

### Input (DTO)
- **`PlanDayDto`**:
  - `target_date: date` (必須: プランニング対象日)
  - `force_sync: bool` (任意, default=True: Google Calendarへの同期を行うか)
- **`SyncWorklogsDto`**:
  - `target_date: Optional[date]` (任意: 指定日付のブリーフィングのみ回収、未指定時は全ファイルをスキャン)

### Output (DTO)
- **`DailyBriefing`**:
  - `target_date: date`
  - `events: List[CalendarEvent]` (配置された全スケジュールブロック)
  - `warning_flags: List[str]` (例: `"W_ratio_low"`, `"DeadlineExceededWarning"`)
  - `content_markdown: str` (Mobile Vaultに配信されるMarkdown文字列)
- **`SyncWorklogsResult`**:
  - `processed_files_count: int`
  - `completed_task_ids: List[str]`
  - `recorded_worklogs_count: int`

### Exceptions (ドメインエラー)
- **`PlanningException`**: スケジューリング計算時の致命的破綻
- **`CalendarSyncException`**: Google Calendar API連携時の認証・通信エラー

---

## 3. Scenarios (受入・テスト要求シナリオ - 6大観点マトリクス)

### ① 正常系 (Happy Path)
- `[TM-PLAN-01]`: Task Registryに「今日やるべき[M][S][W]タスク」が存在するとき、`[W]` ブロック（最低1時間）が最優先で配置され、`[Energy: High]` なタスクが午前のブロックに配置されること。また、すべてのスケジュールは活動時間（05:00-20:00）内でのみ生成されること。
- `[TM-PLAN-07]`: 割り当て可能な空き時間のうち、20%が自己研鑽などの中長期タスク（`[S]`タスク）のために強制的にブロックされること。
- `[TM-PLAN-10]`: 午後(13:00〜15:00)には `[Energy: Low]` または `[W]` のみが配置されること。
- `[TM-PLAN-11]`: 活動終了の最後の30分間は「明日の計画とクールダウン（シャットダウン・リチュアル）」のための固定ブロックとなること。
- `[TM-SYNC-01]`: `plan_day` によって `DailyBriefing` が生成され、固定枠と流動枠のパズルが完了した際、`CalendarRepository` を通じて外部カレンダーにブロック情報が一方向同期（Reconciliation）されること。
- `[TM-SYNC-03]`: `plan_day` によって `DailyBriefing` が生成された際、`MobileVaultGateway` を通じて計画されたタスク一覧が所定のディレクトリにMarkdown形式（`Briefing_YYYY-MM-DD.md`）で配置・上書きされること。
- `[TM-SYNC-04]`: `sync_worklogs` 処理により、Mobile Vault上の `Briefing_YYYY-MM-DD.md` から `- [x]` のマークがついたタスクを抽出し、該当タスクの `TaskStatus` を `COMPLETED` に更新し、実績を `Worklog` に記録した上で、回収済みファイルを自動物理削除（Leave No Trace）すること。

### ② 冪等性・再実行 (Idempotency & Lifecycle)
- `[TM-PLAN-14]`: 同一日付に対して `plan_day` が複数回実行（再生成・再計画）されても、タスク・スケジュール・カレンダー同期内容・Mobile Vault Markdownに重複が発生せず冪等（Idempotent）であること。定期タスク（`RECURRING`）は動的SoRから評価され、DBに保存された過去インスタンスと多重化しないこと。
- `[TM-PLAN-15]`: 固定時間定期タスク（`fixed_time`）は定義された時間枠（例: 07:00-09:00）に必ず配置され、再実行によって夜間等の空き時間に押し出されたり上書きされたりしないこと。

### ③ 境界値・日跨ぎ (Boundary & Midnight)
- `[TM-PLAN-02]`: WIP_LIMIT（3つ）を超えるタスクはスケジュールから弾かれること。
- `[TM-PLAN-04]`: 該当タスクのLFD（限界期限）超過時に `DeadlineExceededWarning` フラグが立つこと。
- `[TM-PLAN-09]`: ディープワークが90分継続した地点で、強制的にブレイクまたは低負荷/`[W]`タスクが挿入されること。
- `[TM-PLAN-12]`: 午前中の Shallow Work は拒絶されるか、午後に回されること。
- `[TM-PLAN-16]`: タスクが0件または空の場合でも、活動時間（05:00-20:00）の範囲内で固定定期タスクのみで構成された有効なスケジュールが生成されること。

### ④ 外部同期・差分調停 (Reconciliation & Drift)
- `[TM-SYNC-02]`: 外部イベント（会議等）はGoogle CalendarをSoRとしてRead-Onlyで扱い、内部ルーティンはDBをSoRとしてWrite権限で動的配置されること。DB側のルーティンは有効期間内のみ配置されること。
- `[TM-PLAN-13]`: 外部の「時間指定イベント」は物理的な壁として扱い、外部の「終日イベント（有休等）」や日本の祝日は日のコンテキスト（`day_context="HOLIDAY"`）を切り替えるメタデータとして解釈し、平日専用タスクを除外すること。

### ⑤ 異常系・耐障害性 (Fault Tolerance & Partial Failure)
- `[TM-PLAN-03]`: `[W]` タスクの割合が20%未満の場合、返却される `DailyBriefing` の `warning_flags` に `"W_ratio_low"` がセットされること。
- `[TM-PLAN-06]`: 依存先タスクが未完了の未Readyタスクは完全に除外されること。
- `[TM-PLAN-08]`: 目的(Areas)に紐付いていない孤立タスクは除外されること。
- `[TM-SYNC-05]`: Mobile Vault の Markdown 上で一部の行やIDコメントが破損・手動削除されていた場合でも、`sync_worklogs` がクラッシュせず、正常な行のみを回収してログを記録すること。

### ⑥ ドメイン不変条件 (Invariants)
- `[TM-PLAN-05]`: タスクが自動バッチ化され、1日の「深い⇔浅い」の往復が最大3回以内に収まること。
- `[TM-PLAN-17]`: 生成されたスケジュール内の全ブロックにおいて、時間帯の不正な重複（Overlap）が絶対に存在しないこと。

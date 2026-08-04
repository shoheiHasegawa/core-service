# Mobile Vault 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜ非同期ファイル連携（Vault）なのか**:
  - モバイル端末（iPhone/Obsidian等）からの素早い思考メモ投下と、デスクトップ/Agentic OS側の非同期な計算・処理を物理的に分離（疎結合化）するため。
- **なぜ処理後の即時破棄（Leave No Trace）なのか**:
  - Vaultに処理済みのメモや画像が残り続けると、未処理アイテムとの混同や二重取り込み（ゴーストデータ）が発生するため、処理完了時（idea/task/delete）はVault上の原本ファイルを即時物理削除する。
- **なぜダッシュボード配置は完全上書き（洗い替え）なのか**:
  - デイリーブリーフィング等のダッシュボードは「その時点の最新状態」を反映するビューであり、追記ではなく全体を洗い替え（上書き保存）することで、同一日に再実行された場合でも常に最新の単一ファイルとして冪等性を保証するため。
- **なぜ厳格なアクションバリデーションなのか**:
  - 不正なアクション名（タイポ等）によるサイレントな処理スキップ（未処理データの消失）を防ぎ、異常なデータに即座に気づけるよう例外（`ValueError`）を発生させる。
- **なぜ画像リンクのマルチフォーマット抽出なのか**:
  - Obsidian標準のWikiLink形式（`![[image.png]]`）とCommonMark標準形式（`![alt](image.png)`）の双方が混在するモバイル環境において、添付画像の取りこぼしを防ぎSecond Brain（Zettelkasten）へのアセット移行を完全自動化するため。

---

## 2. Contract (I/O Types & Stubs)

### Input & Parameters
- **`PeekInboxUseCase.execute() -> list[dict[str, Any]]`**
  - 入力なし（Vault内の未処理ファイルをスキャン）
- **`ProcessInboxItemUseCase.execute(item_id: str, action: str, title: str = "", tags: list[str] | None = None, energy_level: str | None = None) -> bool`**
  - `item_id`: 処理対象ファイル名（例: `quick_note.md`）
  - `action`: `"idea"` | `"task"` | `"delete"` (必須)
  - `title`: 指定時はノート/タスクのタイトル。空文字の場合は `item_id` をフォールバック利用。
  - `tags`: ノート登録時のタグ一覧（`action="idea"` 時に適用）
  - `energy_level`: タスク登録時のエネルギー水準（`"High"` の場合 `TaskCategory.MUST`、それ以外は `TaskCategory.SHOULD`）
- **`PlaceDashboardUseCase.execute(title: str, content: str) -> str`**
  - `title`: 出力ファイル名（例: `Briefing_2026-08-03.md`）
  - `content`: Markdown本文

### Output
- **`PeekInboxUseCase.execute()`**:
  - 要素の型: `{"item_id": str, "content": str, "images": list[dict[str, str]]}`
  - `images` 要素: `{"name": str, "path": str}`
- **`ProcessInboxItemUseCase.execute()`**:
  - `bool`: 処理成功時は `True`、対象アイテムが存在しない場合は `False`。
- **`PlaceDashboardUseCase.execute()`**:
  - `str`: 配置されたダッシュボードファイルの絶対パス。

### Exceptions (エラー・例外設計)
- 原則として Python 標準例外を使用する。
- **`ValueError`**: `action` に `"idea"`, `"task"`, `"delete"` 以外の無効な文字列が指定された場合に送出。ディレクトリトラバーサル等の不正パスを検知した場合に送出。

---

## 3. Scenarios (受入・テスト要求シナリオ - 6大観点マトリクス)

### ① 正常系 (Happy Path)
- `[MV-RECV-01]`: `PeekInboxUseCase` により、Vault内の未処理Inboxアイテム（Markdownメモおよび添付画像）の一覧が副作用なく（Read-onlyで）取得できること。
- `[MV-RECV-02]`: `ProcessInboxItemUseCase` により、指定したInboxアイテムが `idea`（Second Brainへの登録＋画像コピー）、`task`（Task DBへの登録）、`delete`（破棄）のアクションに応じて正しく振り分けられ、処理完了後にVaultから原本ファイルが自動削除されること。
- `[MV-PLACE-01]`: `PlaceDashboardUseCase` により、指定されたタイトルとMarkdown内容がVaultへ正常に配置・保存され、配置先ファイルパスが返却されること。

### ② 冪等性・再実行 (Idempotency & Lifecycle)
- `[MV-IDEM-01]`: 同一Inboxアイテムに対して二重に `ProcessInboxItemUseCase` が実行された場合、2回目は対象が存在しないため安全に `False` を返し、タスクやノートの重複登録が発生しないこと。
- `[MV-IDEM-02]`: 既に同名ファイルが存在する状態で `PlaceDashboardUseCase` を実行した場合、安全に洗い替え（完全上書き保存）され、ファイル重複や追記エラーが発生せず冪等であること。

### ③ 境界値・日跨ぎ (Boundary & Defaults)
- `[MV-BOUND-01]`: Vault内に未処理Inboxアイテムが0件の場合、`PeekInboxUseCase` が空リスト `[]` を安全に返し例外が発生しないこと。
- `[MV-BOUND-02]`: 添付画像を含まないInboxアイテム（画像0件）に対して `ProcessInboxItemUseCase`（`idea`/`task`/`delete`）が正常に完遂すること。
- `[MV-BOUND-03]`: `title` が空文字（`""`）の状態で `ProcessInboxItemUseCase` を実行した場合、`item_id` がフォールバックタイトルとして採用されること。

### ④ 外部同期・差分調停 (Reconciliation & Formats)
- `[MV-RECON-01]`: Markdown本文中にObsidian形式（`![[img.png]]`）と標準Markdown形式（`![alt](img.png)`）が混在している場合でも、すべての添付画像参照が抽出され、Second Brainへの移行および削除が行われること。

### ⑤ 異常系・耐障害性 (Fault Tolerance & Partial Failure)
- `[MV-FAULT-01]`: `ProcessInboxItemUseCase` に対し、`idea`, `task`, `delete` 以外の未知のアクションが指定された場合、サイレントに完了せず `ValueError` が送出され、ファイルが保全されること。
- `[MV-FAULT-02]`: Markdown本文中に画像参照が記述されているがVault上に実画像ファイルが存在しない場合（欠損時）、エラーで全体処理を中断せず、存在する画像のみコピーし、ノート/タスク登録と原本Markdown削除が安全に完遂すること。

### ⑥ ドメイン不変条件 (Domain Invariants)
- `[MV-INVAR-01]`: （Leave No Trace）処理が成功したInboxアイテムおよび抽出画像はVault内に残留せず即時削除され、処理失敗・例外送出時には原本が保全されること。
- `[MV-INVAR-02]`: （Read-only 保証）`PeekInboxUseCase` の実行前後でVault内のファイル内容および状態が一切変更されないこと。

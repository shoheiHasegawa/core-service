# Mobile Vault 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜ非同期ファイル連携（Vault）なのか**:
  - モバイル端末（iPhone/Obsidian等）からの素早い思考メモ投下と、デスクトップ/Agentic OS側の非同期な計算・処理を物理的に分離（疎結合化）するため。
- **なぜ処理後の即時破棄（Leave No Trace）なのか**:
  - Vaultに処理済みのメモや画像が残り続けると、未処理パケットとの混同や二重取り込み（ゴーストデータ）が発生するため、処理完了時（idea/task/delete）はVault上の原本ファイルを即時物理削除する。
- **なぜ厳格なアクションバリデーションなのか**:
  - 不正なアクション名（タイポ等）によるサイレントな処理スキップ（未処理データの消失）を防ぎ、異常なデータに即座に気づけるよう例外（`ValueError`）を発生させる。

---

## 2. Contract (I/O Types & Exceptions)

### UseCases & Functions
- **`PeekInboxUseCase.execute() -> List[Dict[str, Any]]`**:
  - 未処理パケットの一覧を返す。
  - 返却要素: `{"item_id": str, "content": str, "images": List[Dict[str, str]]}`
- **`ProcessInboxItemUseCase.execute(item_id: str, action: str, title: str = "", tags: list[str] = None, energy_level: str = None) -> bool`**:
  - `action`: `"idea"` | `"task"` | `"delete"` (必須)
  - `item_id`: 処理対象ファイル名
  - 返却値: 処理成功時は `True`、対象パケットが存在しない場合は `False`。
- **`PlaceDashboardUseCase.execute(title: str, content: str) -> str`**:
  - `title`: 出力ファイル名 (例: `Briefing_2026-08-02.md`)
  - `content`: Markdown本文
  - 返却値: 配置されたファイルの絶対パス。

### Exceptions (例外定義)
- **`ValueError`**: `action` に `"idea"`, `"task"`, `"delete"` 以外の無効な文字列が渡された場合に送出。

---

## 3. Scenarios (テスト要求シナリオ)

### 正常系 (Happy Path)
- `[MV-RECV-01]`: `PeekInboxUseCase` により、Vault内の未処理パケット（Markdownメモおよび添付画像）の一覧が副作用なく（Read-onlyで）取得できること。
- `[MV-RECV-02]`: `ProcessInboxItemUseCase` により、指定したパケットが `idea`（Second Brainへの登録＋画像移動）、`task`（Task DBへの登録）、`delete`（破棄）のアクションに応じて正しく振り分けられ、処理完了後にVaultから原本ファイルが自動削除されること。
- `[MV-PLACE-01]`: `PlaceDashboardUseCase` により、指定されたタイトルとMarkdown内容がVaultへ正常に配置・保存され、ファイルパスが返却されること。
- `[MV-PLACE-02]`: `PlaceDashboardUseCase` により、同名のダッシュボードファイルが既に存在する場合であっても、安全に上書き保存されること。

### 異常系 / エッジケース (Edge Cases)
- `[MV-RECV-03]`: `ProcessInboxItemUseCase` に対し、`idea`, `task`, `delete` 以外の未知のアクションが指定された場合、サイレントに完了せず `ValueError` が送出されること。

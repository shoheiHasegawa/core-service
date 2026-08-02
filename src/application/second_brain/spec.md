# Second Brain (Zettelkasten) 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜ3層のZettelkastenノート構造（Inbox / Sense Making / Permanent）なのか**:
  - 粗削りなアイデア（Inbox）から、文脈整理（Sense Making）、そして普遍的な知識の結晶（Permanent Note）へと段階的に蒸留し、思考の純度を高めるため。
- **なぜInbox登録時にToDoタスクを自動発行するのか**:
  - Inboxは一時的な保管場所（バッファ）であり、放置による死蔵（Inbox Bankruptcy）を防ぐため、登録時に「メモをPermanent Noteへ蒸留・昇華するための消化タスク（`Process idea: {タイトル}`）」をタスク管理システム（`tasks` DB）に自動発行する。
- **なぜFrontmatterおよび構造化見出しのバリデーション（監査）を行うのか**:
  - タイトル、タグ、Claim（主張）、Context（背景）、Connections（リンク）などのメタデータを厳格に維持し、将来のAIエージェントによるナレッジ検索・推論の精度を担保するため。
- **なぜディレクトリトラバーサル防御を行うのか**:
  - 外部入力や不正なファイル名により、Second Brainの管理外領域のファイルを読み取られたり上書き破壊されたりするセキュリティリスクを完全に遮断するため。

---

## 2. Contract (I/O Types & Exceptions)

### DTOs
- **`RegisterInboxNoteDto`**:
  - `title: str` (必須: ノートタイトル)
  - `content: str` (必須: メモ本文)
  - `tags: Optional[List[str]]` (任意: タグ一覧)
- **`RegisterSenseMakingNoteDto`**:
  - `title: str` (必須: ノートタイトル)
  - `content: str` (必須: 本文)
  - `source: str` (任意, default="": 出典・情報源)
  - `tags: Optional[List[str]]` (任意: タグ一覧)
- **`RegisterPermanentNoteDto`**:
  - `title: str` (必須: 永久保存版タイトル)
  - `claim: str` (必須: 核となる主張・知見)
  - `context: str` (必須: 背景と深掘り)
  - `connections: str` (必須: 関連ノートへのリンク)
  - `tags: Optional[List[str]]` (任意: タグ一覧)

### UseCases
- **`RegisterInboxNoteUseCase.execute(dto: RegisterInboxNoteDto) -> bool`**:
  - InboxディレクトリにMarkdownノートを保存し、タスクDBに `Process idea: {title}` を登録する。
- **`RegisterSenseMakingNoteUseCase.execute(dto: RegisterSenseMakingNoteDto) -> bool`**:
  - Sense Makingディレクトリに所定のテンプレートでフォーマットしたノートを保存する。
- **`RegisterPermanentNoteUseCase.execute(dto: RegisterPermanentNoteDto) -> bool`**:
  - 構造化見出し（Claim / Context / Connections）を持つPermanentノートを保存する。
- **`SearchNotesUseCase.execute(query: str) -> List[str]`**:
  - 指定されたクエリに合致するMarkdownファイル名の一覧を返却する（該当なし時は空リスト `[]`）。
- **`AuditZettelkastenRulesUseCase.execute() -> List[str]`**:
  - 全ノートを検証し、禁止パターン等の違反メッセージ一覧を返却する（違反なし時は空リスト `[]`）。

---

## 3. Scenarios (テスト要求シナリオ)

### 正常系 (Happy Path)
- `[SB-INBOX-01]`: `RegisterInboxNoteUseCase` により、指定されたタイトル・本文のInboxノートが生成・保存され、タスク管理DBに `Process idea: {title}` タスクが自動発行されること。
- `[SB-SENSE-01]`: `RegisterSenseMakingNoteUseCase` により、所定のテンプレートに従いSense MakingディレクトリにMarkdownノートが保存されること。
- `[SB-PERM-01]`: `RegisterPermanentNoteUseCase` により、Claim / Context / Connections の見出しを持つPermanentノートが保存されること。
- `[SB-SEARCH-01]`: `SearchNotesUseCase` により、検索クエリに合致するノート一覧が正しく取得できること。
- `[SB-AUDIT-01]`: `AuditZettelkastenRulesUseCase` により、ディレクトリ内のノート群が走査され、禁止パターンを含むファイルが違反として検知されること。

### 異常系 / セキュリティ防御 (Security & Edge Cases)
- `[SB-NOTE-04]`: 許可されていないパス（`../` によるディレクトリトラバーサル）からのファイル読み込みがブロックされ、エラーとなること。
- `[SB-NOTE-05]`: アセットコピー処理において、ディレクトリトラバーサルを伴うパスへのコピーがブロックされ、エラーとなること。
- `[SB-NOTE-06]`: アセットコピー処理において、コピー先に既に同名ファイルが存在する場合に安全にエラーが発生すること。

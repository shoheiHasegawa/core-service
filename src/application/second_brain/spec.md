# Second Brain (Zettelkasten) 仕様書 (spec.md)

## 1. Design Decisions & Rationale (設計根拠)

- **なぜ3層のZettelkastenノート構造（Inbox / Sense Making / Permanent）なのか**:
  - 粗削りなアイデア（Inbox）から、文脈整理（Sense Making）、そして普遍的な知識の結晶（Permanent Note）へと段階的に蒸留し、思考の純度を高めるため。
- **なぜInbox登録時にToDoタスクを自動発行するのか**:
  - Inboxは一時的な保管場所（バッファ）であり、放置による死蔵（Inbox Bankruptcy）を防ぐため、登録時に「メモをPermanent Noteへ蒸留・昇華するための消化タスク（`Process idea: {タイトル}`）」をタスク管理システム（`tasks` DB）に自動発行する。
- **なぜFrontmatterおよび構造化見出しのバリデーション（監査）を行うのか**:
  - タイトル、タグ、Claim（主張）、Context（背景）、Connections（リンク）などのメタデータを厳格に維持し、将来のAIエージェントによるナレッジ検索・推論の精度を担保するため。
- **なぜ検索クエリの空文字を契約違反（ValueError）とするのか**:
  - 空白や空文字での検索は呼び出し元のバグまたは意図しない不正入力（契約違反）であり、サイレントに空リストや全件を返却するのではなく、Fail-Fastの原則に従い即座に `ValueError` を送出することで契約を明確化・単純化する。
- **なぜディレクトリトラバーサル防御を行うのか**:
  - 外部入力や不正なファイル名により、Second Brainの管理外領域のファイルを読み取られたり上書き破壊されたりするセキュリティリスクを完全に遮断するため。

---

## 2. Contract (I/O Types & Stubs)

### Input (DTO / Command)

- **`RegisterInboxNoteDto`**:
  - `title: str` (必須: ノートタイトル、空文字不可)
  - `content: str` (必須: メモ本文、空文字不可)
  - `tags: Optional[List[str]]` (任意: タグ一覧、デフォルト空リスト)
- **`RegisterSenseMakingNoteDto`**:
  - `title: str` (必須: ノートタイトル、空文字不可)
  - `content: str` (必須: 本文、空文字不可)
  - `source: str` (任意: 出典・情報源、デフォルト `""`)
  - `tags: Optional[List[str]]` (任意: タグ一覧、デフォルト空リスト)
- **`RegisterPermanentNoteDto`**:
  - `title: str` (必須: 永久保存版タイトル、空文字不可)
  - `claim: str` (必須: 核となる主張・知見、空文字不可)
  - `context: str` (任意: 背景と深掘り、デフォルト `""`)
  - `connections: str` (任意: 関連ノートへのリンク、デフォルト `""`)
  - `tags: Optional[List[str]]` (任意: タグ一覧、デフォルト空リスト)

### Output / UseCases

- **`RegisterInboxNoteUseCase.execute(dto: RegisterInboxNoteDto) -> bool`**:
  - InboxディレクトリにMarkdownノートを保存し、タスクDBに `Process idea: {title}` を登録する。
- **`RegisterSenseMakingNoteUseCase.execute(dto: RegisterSenseMakingNoteDto) -> bool`**:
  - Sense Makingディレクトリに所定のテンプレートでフォーマットしたノートを保存する。
- **`RegisterPermanentNoteUseCase.execute(dto: RegisterPermanentNoteDto) -> bool`**:
  - 構造化見出し（Claim / Context / Connections）を持つPermanentノートを保存する。
- **`SearchNotesUseCase.execute(query: str) -> List[str]`**:
  - 指定されたクエリに合致するMarkdownファイル名（ベースネーム）の一覧を返却する（該当なし時は空リスト `[]`）。
- **`AuditZettelkastenRulesUseCase.execute() -> List[str]`**:
  - 全ノートを走査・検証し、禁止パターンやタグフォーマット等の違反メッセージ一覧を返却する（違反なし時は空リスト `[]`）。

### Exceptions (エラー・例外設計)

- 原則として Python 標準例外（`ValueError`, `FileNotFoundError`, `FileExistsError` 等）を使用する（`docs/rules/error_handling.md` 準拠）。
- **`ValueError`**:
  - 必須フィールド（`title`, `content`, `claim`）が空文字または空白のみの場合
  - 検索クエリ（`query`）が空文字または空白のみの場合
  - ディレクトリトラバーサル攻撃を検知した場合
- **`FileExistsError`**:
  - 保存先またはアセットコピー先に同名ファイルが既に存在する場合
- **`FileNotFoundError`**:
  - 参照先のテンプレートファイル等が存在しない場合

---

## 3. Scenarios (受入・テスト要求シナリオ - 6大観点マトリクス)

### ① 正常系 (Happy Path)
- `[SB-INBOX-01]`: `RegisterInboxNoteUseCase` により、指定されたタイトル・本文・タグのInboxノートがMarkdownとして生成・保存され、タスク管理DBに `Process idea: {title}` タスクが自動発行されること。
- `[SB-SENSE-01]`: `RegisterSenseMakingNoteUseCase` により、所定のテンプレートに従いSense MakingディレクトリにMarkdownノートが保存されること。
- `[SB-PERM-01]`: `RegisterPermanentNoteUseCase` により、Claim / Context / Connections の構造化見出しを持つPermanentノートが保存されること。
- `[SB-SEARCH-01]`: `SearchNotesUseCase` により、有効な検索クエリに合致するノート一覧（ファイル名）が正しく取得できること（該当なし時は空リスト `[]`）。
- `[SB-AUDIT-01]`: `AuditZettelkastenRulesUseCase` により、ディレクトリ内のノート群が走査され、禁止パターンを含むファイルが違反として検知されること。

### ② 冪等性・再実行 (Idempotency & Lifecycle)
- `[SB-IDEMP-01]`: 同一タイトルのノートを連続して登録しようとした場合、2回目以降は既存ノートを破壊せず `FileExistsError` を送出して即時停止し、タスクの多重発行も行われないこと。
- `[SB-IDEMP-02]`: `AuditZettelkastenRulesUseCase` は読み取り専用であり、複数回連続実行しても内部状態やファイルに一切の副作用を与えないこと。

### ③ 境界値・日跨ぎ (Boundary & Midnight)
- `[SB-BOUND-01]`: ノート登録（Inbox / SenseMaking / Permanent）において、`title` が空文字（`""`）または空白のみ（`"   "`）の場合、即座に `ValueError` を送出すること。
- `[SB-BOUND-02]`: Permanentノート登録において、`claim` が空文字または空白のみの場合、即座に `ValueError` を送出すること。
- `[SB-BOUND-03]`: `SearchNotesUseCase` において、`query` が空文字（`""`）または空白のみ（`"   "`）の場合、契約違反として即座に `ValueError` を送出すること。
- `[SB-BOUND-04]`: 日跨ぎ（00:00跨ぎ）のタイミングでノートを登録した場合でも、Frontmatterの日付（`{{date}}`）が実行時点のタイムスタンプで安全に記録されること。

### ④ 外部同期・差分調停 (Reconciliation & Drift)
- `[SB-RECON-01]`: 手動で外部エディタにより作成・変更されたノート群に対しても、`AuditZettelkastenRulesUseCase` および `SearchNotesUseCase` が正しく走査・検索・ルール検証を行えること。

### ⑤ 異常系・耐障害性 (Fault Tolerance & Partial Failure)
- `[SB-NOTE-04]`: 許可されていないパス（`../` によるディレクトリトラバーサル）からのファイル読み込み（`read`）がブロックされ、`ValueError` となること。
- `[SB-NOTE-05]`: アセットコピー処理（`copy_asset`）において、ディレクトリトラバーサルを伴うパスへのコピーがブロックされ、`ValueError` となること。
- `[SB-NOTE-06]`: アセットコピー処理において、コピー先に既に同名ファイルが存在する場合に `FileExistsError` が発生すること。
- `[SB-FAULT-01]`: テンプレートファイルが存在しない場合、`FileNotFoundError` となり不正なファイル保存が行われないこと。
- `[SB-FAULT-02]`: 不正なタグフォーマット（階層構造でないタグ等）やID欠損を含むノートが存在する場合、`AuditZettelkastenRulesUseCase` で該当のエラーメッセージが正確にリストアップされること。

### ⑥ ドメイン不変条件 (Domain Invariants)
- `[SB-INVAR-01]`: すべてのノート保存処理において、生成されるファイル名にファイルシステム上の禁止文字（`/\*?"<>|`）が含まれず、安全にサニタイズされた `.md` ファイルとして永続化されること。
- `[SB-INVAR-02]`: `LocalFileSecondBrainGateway` は管理ルートディレクトリ（`base_path`）の配下にないパスへのアクセスを一切許容しないこと（ディレクトリトラバーサルの完全遮断）。

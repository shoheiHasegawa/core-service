# Specification: Mobile Vault Context

## 1. Domain Overview
*   **Domain**: `you_inc` (Personal Agentic OS)
*   **Context**: Mobile Vault Integration
*   **Responsibility**: ユーザーがモバイル端末（iPhone等）で利用している「Vault（iCloud/Obsidian等）」と、Agentic OS間のデータの非同期なやり取りを管理する。

## 2. Ubiquitous Language (ユビキタス言語)
*   **Vault (保管庫)**: モバイル端末とAgentic OSを繋ぐ非同期のファイル連携領域。
*   **Packet (パケット)**: ユーザーがモバイルからVaultに投げ込んだ未処理の思考の断片（Markdownメモ＋画像等）。
*   **Dashboard (ダッシュボード)**: Agent側からユーザーに向けてVaultへ書き出す、読み取り専用のサマリ画面。
*   **Briefing (ブリーフィング)**: Task ManagementコンテキストにおいてVaultへ配置される特定のダッシュボード。

## 3. Scenarios (Use Cases)

### [MV-RECV-01] Peek Mobile Inbox (未処理パケットの一覧取得)
*   **Target**: `PeekMobileInboxUseCase`
*   **Process**:
    1. `PacketReceiver` 経由で、Vault内の未処理パケットの一覧を取得する。
    2. 各パケットの内容（テキスト）と、関連する画像パス（Attachment）の情報を読み取る。
    3. 副作用（ファイルの削除や移動）は一切発生させない（Read-only）。
*   **Output**: 読み取られたパケット情報（ID, 内容, 画像パスのリスト）のコレクション。

### [MV-RECV-02] Process Mobile Packet (未処理パケットの選択的処理)
*   **Target**: `ProcessMobilePacketUseCase`
*   **Input**: 処理対象のパケットID (`packet_id: str`)、アクション (`action: str` - idea/task/delete)、メタデータ (`title`, `tags`, `energy_level`)
*   **Process**:
    1. 対象パケットを読み取り、`action` に応じて以下を実行する:
       - **idea**: `SecondBrainService` 経由でアイデアノートとして登録。
       - **task**: `TaskOperationsService` 経由でタスクとして登録。
       - **delete**: 登録せず破棄。
    2. `idea` または `task` の場合、パケットに含まれる画像ファイルを `second-brain` の Attachments ディレクトリ等へ安全に移動（コピー＆元ファイル削除）する。
    3. `PacketReceiver.delete_packet(packet_id)` で、処理完了したパケットをVaultから削除する。
*   **Output**: 処理の成功/失敗を表す真偽値 (Boolean)。

### [MV-PLACE-01] Place Dashboard (ダッシュボードの配置)
*   **Target**: `PlaceDashboardUseCase`
*   **Input**: 配置対象のダッシュボードタイトル (`title: str`)、内容のMarkdown文字列 (`content: str`)
*   **Process**:
    1. `DashboardPublisher.publish(title, content)` を呼び出し、Vaultへダッシュボードを配置する。
*   **Output**: 配置されたファイルの絶対パスなど、インフラが決定した識別子（String）。

### [MV-PLACE-02] 異常系: Dashboard配置の上書き処理
*   **事後条件**: ダッシュボードの性質上、既存のファイルが存在する場合は安全に上書き保存されること。（※旧仕様ではエラーにしていましたが、ダッシュボードは定期更新されるため上書きを許容します）

## 4. Architecture & Layered Rules
*   **Domain Separation (Port)**:
    *   `src/domain/mobile_vault/gateway.py` に `PacketReceiver` および `DashboardPublisher` を定義する。ファイルI/Oの概念（filename, read_text）を極力排除する。
*   **Application (Use Cases)**:
    *   `src/application/mobile_vault/` 配下に `peek_mobile_inbox_usecase.py`, `process_mobile_packet_usecase.py`, `place_dashboard_usecase.py` を独立して実装し、SRPを満たす。
*   **Infrastructure (Adapter)**:
    *   `src/infrastructure/mobile_vault/local_file_mobile_vault_gateway.py` は、Domain層のインターフェースを実装する。
    *   `src/infrastructure/task_management/briefing_gateway.py` は `DashboardPublisher` を利用してブリーフィングを書き出す。

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

### [MV-RETRIEVE-01] Retrieve Unprocessed Packets (未処理パケットの回収)
*   **Target**: `RetrievePacketsUseCase`
*   **Process**:
    1. `PacketReceiver` 経由で、Vault内の未処理の `Packet` のリストを取得する。
    2. 取得した `Packet` ごとに以下を実行する:
       a. `MarkdownImageParser` 等を用いて画像リンクを抽出・処理する。
       b. 処理後、`TaskRepository` を用いて、パケットの処理タスク（Task）を生成・保存する。
       c. `PacketReceiver.delete_packet(packet)` で、回収完了したパケットをVaultから削除する。
*   **Output**: 成功裏に回収されたパケットの数（Int）。

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
    *   `src/application/mobile_vault/usecases/` 配下に `retrieve_packets_usecase.py` と `place_dashboard_usecase.py` を独立して実装し、SRPを満たす。
*   **Infrastructure (Adapter)**:
    *   `src/infrastructure/mobile_vault/local_file_mobile_vault_gateway.py` は、Domain層のインターフェースを実装する。
    *   `src/infrastructure/task_management/briefing_gateway.py` は `DashboardPublisher` を利用してブリーフィングを書き出す。

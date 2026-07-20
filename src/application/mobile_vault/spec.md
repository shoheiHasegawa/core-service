# Specification: MobileVaultService

## 1. Domain Overview
*   **Domain**: `you_inc` (Personal Agentic OS)
*   **Context**: Mobile Vault Integration
*   **Service Name**: `MobileVaultService`
*   **Responsibility**: ユーザーがモバイル端末（iPhone等）で利用している「Mobile Vault（iCloud/Obsidian等）」と、Agentic OS間のデータのやり取り（回収および配置）を抽象化して管理する単一の窓口。

## 2. Ubiquitous Language (ユビキタス言語)
*   **Mobile Vault**: モバイル端末からアクセス可能なMarkdownノート群の保存領域。
*   **Packet**: ユーザーがMobile Vaultに雑多に入力した未処理のメモと、それに関連する画像などのまとまり。
*   **Retrieve (回収する)**: Mobile Vaultに存在する未処理のPacketをPC側（Agent側）のQueueに取り込むこと。二重処理を防ぐため、取り込みと同時に元のファイルはMobile Vaultから削除される。
*   **Place (配置する)**: Agentが生成したMarkdown等（ダッシュボードやノート）を、Mobile Vault上の指定されたパスに書き込むこと。

## 3. Scenarios (Use Cases)

### [MV-FILE-01] Retrieve Unprocessed Packets (未処理パケットの回収)
*   **Input**: (なし。ディレクトリパスは `MobileVaultConfig` からDIされる)
*   **Process**:
    1. Infrastructure層のRepository経由で、Inbox内の全 `.md` ファイルパスを取得する。
    2. Domain層の `MarkdownImageParser` 等を用いて、Markdown文字列から画像リンクを抽出する。
    3. `Packet` エンティティとして生成し、一意なID（UUID等）を採番する。
    4. Infrastructure層にパケットと画像の移動（Queueへのバンドル作成）を指示する。
    5. 移動完了後、元のファイルをMobile Vaultから削除する。
*   **Output**: 成功裏に回収されたパケットバンドルの数（Int）。

### [MV-FILE-02] Place Dashboard (ダッシュボードの配置)
*   **Input**: 配置対象のMarkdown文字列 (`content`)、配置先のディレクトリパス (`dashboard_dir`)、ファイル名 (`filename.md`)
*   **Process**:
    1. 指定されたMobile Vaultのダッシュボード配置用ディレクトリが存在しない場合は作成する。
    2. 指定されたファイル名で、ダッシュボードの内容（Markdown）を上書き保存する。
*   **Output**: 配置されたファイルの絶対パス（String）。

### [MV-FILE-03] 異常系: ファイル上書き保存のエラー
*   **事後条件**: 既存のファイルを上書きしようとした場合、`FileExistsError` が発生すること。

### [MV-FILE-04] 異常系: ファイル移動先の上書きエラー
*   **事後条件**: ファイルの移動先に既にファイルが存在する場合、`FileExistsError` が発生すること。

## 4. Architecture & Layered Rules
*   **Feature-Driven Packaging**: この機能に関連する `service.py`, `config.py`, `spec.md` はすべて `src/application/mobile_vault/` 配下にまとめる。
*   **Service-Config Pattern**: 環境依存のディレクトリパス（`inbox_dir`, `attachments_dir`, `queue_dir`）は `MobileVaultConfig` データクラスに定義し、`MobileVaultService` のコンストラクタで Inject すること。メソッド引数には渡さない。
*   **Domain Separation**: MarkdownのパースロジックやパケットIDの採番処理は、Infrastructure層（Repository）ではなく、Domain層のサービス（例: `MarkdownImageParser`）やエンティティで行うこと。
*   **Infrastructure Adapter**: `icloud_vault_repository.py` は純粋なファイルI/O（読み込み、書き込み、削除、移動）のみを行うこと。

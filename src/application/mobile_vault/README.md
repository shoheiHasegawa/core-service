# Mobile Vault (Context Integration Hub)

## 1. Context & Objective (背景と目的)
- **Why (なぜ必要なのか)**: 社長（ユーザー）が外出先や移動中にモバイル端末（iPhone / Obsidian Vault）から投げ込んだアイデア・タスクメモを、非同期かつ安全にAgentic OS（Second Brain / Task Management）へ取り込み、日々のダッシュボード（ブリーフィング）を端末へ届けるため。
- **What (何を実現するのか)**: モバイル保管庫（Vault）の未処理パケットのプレビュー（Peek）、アクション（idea / task / delete）に応じた自動振り分け・画像退避・原本自動破棄（Leave No Trace）、およびダッシュボード配信・上書き管理を行うステートレスな連携ハブ。

---

## 2. Architecture & Data Flow (アーキテクチャ)

```mermaid
graph TD
    MVS[MobileVaultService]
    MVG[LocalFileMobileVaultGateway]
    SBS[SecondBrainService]
    TOS[TaskOperationsService]
    Parser[MarkdownImageParser]

    MVS -->|1. 未処理パケット一覧取得| MVG
    MVS -->|2. idea: ノート登録 & 画像移動| SBS
    MVS -->|3. task: タスクDB登録| TOS
    MVS -->|4. 原本メモ・画像削除 (Leave No Trace)| MVG
    MVS -->|5. Dashboard配置・上書き| MVG
```

### アーキテクチャ上の責務
1. **ステートレスな振り分けエンジン**: 自身は永続化状態を持たず、モバイルファイルシステムとコアサービス各層を中継する。
2. **Leave No Trace（原本自動破棄）**: パケット処理後は速やかにVault上のメモと一時画像を物理削除し、二重取り込みを根絶する。
3. **安全なアセット移譲**: メモに画像が含まれる場合、Second Brainの添付ファイル領域へ安全に移行する。

---

## 3. Routing & Navigation (関連ファイルへのポインタ)

当機能に関する主要なファイル群へのリンク（ポインタ）。開発やテストを行う際は以下を参照すること。

- **仕様書 (Contract & Scenarios)**: [spec.md](./spec.md)
- **エントリーポイント (Facade / UseCases)**:
  - Facade: [mobile_vault_service.py](./mobile_vault_service.py)
  - パケットプレビュー: [peek_inbox_usecase.py](./peek_inbox_usecase.py)
  - パケット振り分け・処理: [process_inbox_item_usecase.py](./process_inbox_item_usecase.py)
  - ダッシュボード配置: [place_dashboard_usecase.py](./place_dashboard_usecase.py)
- **結合テスト (Integration Tests)**:
  - パケット処理＆画像移行: `tests/integration/mobile_vault/test_mobile_vault_integration.py`
  - ダッシュボード配置＆上書き: `tests/integration/mobile_vault/test_place_dashboard.py`
- **単体テスト (Unit Tests)**:
  - Application: `tests/unit/application/mobile_vault/`
  - Domain: `tests/unit/domain/mobile_vault/`
  - Infrastructure: `tests/unit/infrastructure/local_file/test_local_file_mobile_vault_gateway.py`

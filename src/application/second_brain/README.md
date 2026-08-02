# Second Brain (Zettelkasten Knowledge Engine)

## 1. Context & Objective (背景と目的)
- **Why (なぜ必要なのか)**: 社長（ユーザー）の思考の断片や知見を、一時的な思いつきで終わらせず、普遍的な知識のネットワーク（Zettelkasten）へと体系的に蒸留・蓄積するため。
- **What (何を実現するのか)**: 3層のノート管理（Inbox / Sense Making / Permanent Notes）、Frontmatterおよび構造化見出しのバリデーション、Inbox登録時のTo Doタスク自動発行、およびナレッジの全文検索を担うステートレスな知識管理エンジン。

---

## 2. Architecture & Data Flow (アーキテクチャ)

```mermaid
graph TD
    SBS[SecondBrainService]
    SBG[LocalFileSecondBrainGateway]
    TR[TaskRepository (SQLite)]
    Validator[ZettelkastenValidator]
    Formatter[ZettelkastenFormatter]

    SBS -->|1. Inboxノート保存| SBG
    SBS -->|2. Process idea タスク自動発行| TR
    SBS -->|3. Sense Making / Permanent 整形 & 保存| Formatter
    Formatter --> SBG
    SBS -->|4. Zettelkastenルール監査| Validator
    SBS -->|5. ノート全文検索| SBG
```

### アーキテクチャ上の責務
1. **知識の段階的蒸留**:
   - `00_Inbox/`: 粗削りなアイデアメモの受付領域。
   - `20_Sense_Making/`: コンテキストと論理構造を整理した中間ノート領域。
   - `30_Permanent_Notes/`: Claim（主張）、Context（背景）、Connections（リンク）を持つ完成版ノート領域。
2. **Inbox死蔵防止のタスク発行**: Inbox登録と同時に `Process idea: {タイトル}` タスクを発行し、ユーザーの内省・清書サイクルを強制する。
3. **堅牢なセキュリティ防御**: ディレクトリトラバーサル攻撃や不正なファイル上書きをGateway層で物理ブロックする。

---

## 3. Routing & Navigation (関連ファイルへのポインタ)

当機能に関する主要なファイル群へのリンク（ポインタ）。開発やテストを行う際は以下を参照すること。

- **仕様書 (Contract & Scenarios)**: [spec.md](./spec.md)
- **エントリーポイント (Facade / UseCases)**:
  - Facade: [second_brain_service.py](./second_brain_service.py)
  - Inboxノート登録: [register_inbox_note_usecase.py](./register_inbox_note_usecase.py)
  - Sense Makingノート登録: [register_sense_making_note_usecase.py](./register_sense_making_note_usecase.py)
  - Permanentノート登録: [register_permanent_note_usecase.py](./register_permanent_note_usecase.py)
  - ノート検索: [search_notes_usecase.py](./search_notes_usecase.py)
  - ルール監査: [audit_zettelkasten_rules_usecase.py](./audit_zettelkasten_rules_usecase.py)
- **結合テスト (Integration Tests)**:
  - ライフサイクル＆監査＆セキュリティ: `tests/integration/second_brain/test_integration.py`
- **単体テスト (Unit Tests)**:
  - Application: `tests/unit/application/second_brain/`
  - Domain: `tests/unit/domain/second_brain/`
  - Infrastructure: `tests/unit/infrastructure/local_file/test_local_file_second_brain_gateway.py`

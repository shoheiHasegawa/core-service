# SecondBrainService

## 概要
Agentic OS の中核である「Second Brain」とのやり取りを統括する Application Service です。

## 責務
- `register_knowledge()`: Mobile Vault等から回収したアイデアをZettelkastenの形式に清書し、Inboxに保存する。
- `search_notes()`: 既存のPermanent Notesを検索する。
- `audit_zettelkasten_rules()`: Zettelkastenの規則（フロントマター、禁止リンク等）に違反がないかを監査する。
